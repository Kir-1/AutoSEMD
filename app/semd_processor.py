import re
from typing import Union, Iterator, Iterable

from lxml import etree
from lxml.etree import _Element
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.database import engine, Base
from app.models import SemdProperty, SemdPropertyType, Semd, Semd_SemdProperty
from config.settings import semd_paths, headers_base_value, namespaces, xpath_comment
from head_parsing.utils import timer


class Type:
    """
    Класс для обработки валидации типа с использованием регулярных выражений.
    """

    def __init__(self, regexp: re.Pattern):
        """
        Инициализация объекта Type.

        :param regexp: Регулярное выражение для валидации.
        """
        self.regexp = regexp

    def __call__(self, target: str) -> bool:
        """
        Проверить, соответствует ли целевая строка регулярному выражению.

        :param target: Целевая строка для проверки.
        :return: True, если строка соответствует регулярному выражению, иначе False.
        """
        return self.regexp.search(target) is not None


class SEMDField:
    """
    Класс, представляющий одно поле внутри SEMD.
    """

    def __init__(self, **kwargs):
        """
        Инициализация объекта SEMDField.

        :param kwargs: Аргументы, определяющие атрибуты и значения поля.
        """
        for k, v in kwargs.items():
            setattr(self, k.replace("@", ""), v)
        self.value = kwargs.get("@value", "").replace("{", "").replace("}", "")
        self.type = Type(re.compile(kwargs.get("@type", r"^.+$")))

    def __call__(self, *args, **kwargs) -> bool:
        """
        Валидировать значение поля.

        :return: True, если значение поля соответствует типу, иначе False.
        """
        return self.type(self.value)


class SEMDFields:
    """
    Класс, представляющий коллекцию полей SEMD.
    """

    def __init__(self):
        """
        Инициализация объекта SEMDFields.
        """
        self.semd_fields: list[SEMDField] = []
        self.stuff_to_del = set()

    def append(self, field: dict):
        """
        Добавить новое поле SEMD в коллекцию.

        :param field: Словарь, содержащий атрибуты и значения поля.
        """
        self.semd_fields.append(SEMDField(**field))

    def __iter__(self) -> Iterator[SEMDField]:
        """
        Итерация по коллекции полей SEMD.

        :return: Итератор полей SEMD.
        """
        for idx in sorted(self.stuff_to_del, reverse=True):
            del self.semd_fields[idx]
        self.stuff_to_del.clear()
        return iter(self.semd_fields)

    def __getitem__(self, item: int):
        for idx in self.stuff_to_del:
            del self.semd_fields[idx]
        self.stuff_to_del.clear()

        return self.semd_fields[item]

    def unlink(self, semd_field: SEMDField):
        self.stuff_to_del.add(self.semd_fields.index(semd_field))


class SEMD:
    """
    Класс SEMD представляет сущность для работы с XML SEMD документом.
    Позволяет заполнение XML на основе данных из БД,
    а также обрабатывает создание сериализованного XML файла.

    Attributes:
        code (int): Идентификатор объекта.
        oid (str): Идентификатор объекта (OID).
        xml_path (str): Путь к исходному XML.
        xml_doc (_Element): Загруженный XML документ после обработки.
        _semd_fields (SEMDFields): Список обрабатываемых полей XML.

    Methods:
        _create_header_xml: Создает XML заголовок и инициализирует поля SEMD.
        save: Сохраняет измененный XML документ в файл.
        _encode_name: Кодируем символы специальных знаков для использования в XML.
        _decode_name: Декодирует обратно значения атрибутов.
        _get_first_or_none: Возвращает первый элемент или None из итерируемого.
        create_fields_in_database: Создает соответствующие поля в БД, если они отсутствуют.
    """

    def __init__(self, oid: str, code: int):
        """
        Инициализация объекта SEMD.

        :param oid: Идентификатор объекта (OID).
        :param code: Идентификатор объекта (code).
        """
        self.code = code
        self.oid = oid
        self.xml_path: str = semd_paths.get(self.oid, None)
        self.xml_doc = self._create_header_xml() if self.xml_path else None

    def _create_header_xml(self) -> _Element:
        """
        Создать XML заголовок на основе предопределенных headers_base_value.

        :return: Корневой элемент XML.
        """
        root = etree.parse(self.xml_path)
        self._semd_fields: SEMDFields = SEMDFields()

        # Проход по заголовкам для заполнения полей SEMD и обновления XML
        for header_key, header_value in headers_base_value.items():
            el: Union[_Element, None] = self._get_first_or_none(
                root.xpath(header_key, namespaces=namespaces),
            )
            if el is not None:
                comment = self._get_first_or_none(
                    root.xpath(header_key + xpath_comment, namespaces=namespaces),
                )
                comment = {
                    "text": (
                        comment.text if comment is not None else header_value["comment"]
                    )
                }
                print(header_value["comment"])
                del header_value["comment"]

                if comment is not None:
                    header_value = {
                        key: {
                            **value,
                            "@req": (
                                re.search(r"\[\d+\.\.\d+\]", comment["text"]).group(0)
                                if re.search(r"\[\d+\.\.\d+\]", comment["text"])
                                else "[0..0]"
                            ),
                            "@alias": (
                                re.search(
                                    r"\[\d+\.\.[1-9\*]\](.*)", comment["text"]
                                ).group(1)
                                + " -> "
                                + key
                                if re.search(r"\[\d+\.\.[1\*]\]", comment["text"])
                                else "Not alias"
                            ),
                            "@comment": comment["text"],
                        }
                        for key, value in header_value.items()
                    }
                for attr_name, attr_value in header_value.items():
                    attr_value["@value"] = self._encode_name(
                        "{" + header_key + "@" + attr_name + "}"
                    )
                    self._semd_fields.append(attr_value)
                    if attr_name in el.attrib:
                        el.set(attr_name, attr_value["@value"])
                    elif attr_name == "text":
                        el.text = attr_value["@value"]

        return root

    def save(self):
        """
        Сохранить измененный XML документ в файл.
        """
        with open("target.xml", "wb") as f:
            f.write(
                etree.tostring(
                    self.xml_doc,
                    pretty_print=True,
                    xml_declaration=True,
                    encoding="utf-8",
                )
            )

    @classmethod
    def _encode_name(cls, name: str) -> str:
        """
        Кодирует символы в строке для предотвращения проблем XML.

        :param name: Строка, которую необходимо закодировать.
        :return: Закодированная строка.
        """
        # Добавим комментарий ниже для уточнения причины энкодинга
        # Кодируем символы в их hex-обозначения, чтобы предотвратить конфликты при использовании их в качестве имен XML элементов

        return (
            name.replace("/", "_x2F_")
            .replace(":", "_x3A_")
            .replace("@", "_x40_")
            .replace("[", "_x5B_")
            .replace("]", "_x5D_")
        )

    @classmethod
    def _decode_name(cls, encoded_name: str) -> str:
        # Декодируем обратно в исходные символы
        return (
            encoded_name.replace("_x2F_", "/")
            .replace("_x3A_", ":")
            .replace("_x40_", "@")
            .replace("_x5B_", "[")
            .replace("_x5D_", "]")
        )

    @staticmethod
    def _get_first_or_none(target: Iterable):
        return next(iter(target), None)

    def _delete_tag(self, xpath: str):
        el = self._get_first_or_none(
            self.xml_doc.xpath(
                xpath,
                namespaces=namespaces,
            ),
        )
        if el is not None:
            el.getparent().remove(el)

    def __call__(self) -> _Element:
        """
        Обработать поля SEMD и заполнить их значениями из базы данных.

        :return: Измененный XML документ.
        :raises: ValueError, если валидация одного из полей не удалась.
        """
        for field in self._semd_fields:
            with sessionmaker(bind=engine)() as session:
                semd_property_type = (
                    session.query(SemdPropertyType)
                    .filter_by(
                        id=session.query(SemdProperty)
                        .filter_by(xpath_name=self._decode_name(field.value))
                        .first()
                        .semdPropertyType_id
                    )
                    .first()
                )

                if not (
                    semd_property_type.db_name
                    and semd_property_type.sql_query
                    and semd_property_type.alias
                ) and not (
                    field.req.startswith("[0..0]") or field.req.startswith("[0..*]")
                ):
                    raise ValueError(
                        f"Заполните поля db_name, sql_query или alias для семда. \noid = {self.oid} \ncode = {self.code} \nxpath_name = {self._decode_name(field.value)}"
                    )

                if semd_property_type.sql_query is None:

                    self._delete_tag(
                        self._get_first_or_none(
                            self._decode_name(field.value).split("@"),
                        )
                    )

                    self._semd_fields.unlink(field)
                    continue

                result = (
                    session.connection()
                    .execute(text(semd_property_type.sql_query))
                    .fetchone()
                )
                # TODO: Обработать ошибку что в result может не оказаться атрибута с именем db_name
                if not field.type(
                    str(result.__getattr__(semd_property_type.db_name))
                ) and (
                    field.req.startswith("[0..0]") or field.req.startswith("[0..*]")
                ):
                    self._delete_tag(
                        self._get_first_or_none(
                            self._decode_name(field.value).split("@"),
                        )
                    )
                    self._semd_fields.unlink(field)
                    continue

                # TODO: Обработать ошибку что в result может не оказаться атрибута с именем db_name
                if not field.type(str(result.__getattr__(semd_property_type.db_name))):
                    break
                # TODO: Обработать ошибку что в result может не оказаться атрибута с именем db_name
                field.__setattr__(
                    "in_xml", result.__getattr__(semd_property_type.db_name)
                )
        else:
            temp_xml_doc = etree.tostring(self.xml_doc, encoding="unicode")
            temp_xml_doc = temp_xml_doc.format(
                **{filed.value: filed.in_xml for filed in self._semd_fields}
            )
            self.xml_doc = etree.fromstring(temp_xml_doc)
            return self.xml_doc

        raise ValueError("Валидация не прошла для одного из полей")

    def create_fields_in_database(self) -> None:
        """
        Создает поля в базе данных на основе информации из семантических полей, если они еще не существуют.
        Операция выполняется для четырёх связанных таблиц, обновляя связи для актуализации данных.
        """
        # создание таблиц если их нет
        Base.metadata.create_all(engine)

        for field in self._semd_fields:

            with sessionmaker(bind=engine)() as session:

                # Проверка и вставка данных в Semd
                semd = session.query(Semd).filter_by(oid=self.oid).first()
                if not semd:
                    semd = Semd(oid=self.oid, code=self.code)
                    session.add(semd)
                    session.commit()

                    print(
                        f"В Таблице Semd не найдена запись для Документа с oid = {self.oid} и code = {self.code}"
                    )

                # Проверка и вставка данных в SemdProperty
                semd_property = (
                    session.query(SemdProperty)
                    .filter_by(xpath_name=self._decode_name(field.value))
                    .first()
                )

                if semd_property:
                    semd_semd_property = (
                        session.query(Semd_SemdProperty)
                        .filter_by(semdProperty_id=semd_property.id)
                        .all()
                    )

                    if all(semd.id != el.semd_id for el in semd_semd_property):
                        session.add(
                            Semd_SemdProperty(
                                semd_id=semd.id, semdProperty_id=semd_property.id
                            )
                        )
                        session.commit()
                        print(
                            f"В Таблице Semd_SemdProperty была добавлена запись для Документа с oid = {self.oid}. Alias = {field.alias}; semd_id = {semd.id}; "
                            f"semdProperty_id={semd_property.id}"
                        )
                        continue
                    else:
                        continue

                else:
                    semd_property_type = SemdPropertyType(
                        db_name=None, sql_query_id=None, alias=field.alias, comment=None
                    )
                    session.add(semd_property_type)
                    session.commit()

                    semd_property = SemdProperty(
                        xpath_name=self._decode_name(field.value),
                        semdPropertyType_id=semd_property_type.id,
                    )
                    session.add(semd_property)
                    session.commit()
                    print(
                        f"В Таблице SemdPropertyType была добавлена запись для Документа с oid = {self.oid}. Alias = {semd_property_type.alias}; id = {semd_property_type.id}"
                    )
                    print(
                        f"В Таблице SemdProperty была добавлена запись для Документа с oid = {self.oid} и xpath_name ={self._decode_name(field.value)}. id = {semd_property.id}"
                    )

                # Проверка и вставка данных в Semd_SemdProperty
                semd_semd_property = (
                    session.query(Semd_SemdProperty)
                    .filter_by(semd_id=semd.id, semdProperty_id=semd_property.id)
                    .first()
                )
                if not semd_semd_property:
                    semd_semd_property = Semd_SemdProperty(
                        semd_id=semd.id, semdProperty_id=semd_property.id
                    )
                    session.add(semd_semd_property)
                    session.commit()
