from ge.models import GeStaff
from qdb.models import Staff

source_records = Staff.objects.all()

target_instances = [
    GeStaff(
        qdbName=record.name,
        qdbEmail=record.email
    )
    for record in source_records
]

GeStaff.objects.bulk_create(target_instances)
