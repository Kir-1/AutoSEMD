
from app.semd_processor import SEMD

if __name__ == "__main__":

    semd = SEMD(oid="81", code=122)

    #semd.create_fields_in_database()
    semd()
    # Сохраняем данные
    semd.save()
    print(f"Сохранен объект с OID: {semd.oid}, код: {semd.code}")
