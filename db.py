#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automatic reports dataclasses
@author: Milos.Korenciak@Solargis.com"""


from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
from playhouse.db_url import connect  # we need this to be exposed from the module
from playhouse.fields import CompressedField
import datetime
import os
import peewee as pw


# create DB connection
db_url = os.getenv('DATABASE_URL', "sqlite:///my_database.db")
database = connect(db_url)
TIMEOUT = datetime.timedelta(0, 12*60)  # 12 minutes old tasks are considered to be timeouted
# state constants of the task
REQUEST_RAW = 10
REQUEST_2ND_LEVEL = 20
TEX_RAW = 30
PDF_RAW = 40
PDF_SIGNED = 50


class DBModel(pw.Model):
    """Base class for all DB Object-Relation-Mapped classes"""
    def __str__(self):
        """Default str(obj) handling - default writeout"""
        return str(self._data)

    def to_json(self):
        """Default JSON-ize method"""
        return str(dict(zip(map(str, self._data.keys()), map(str, self._data.values()) )))

    class Meta:
        """Meta class - for configuration of ORM"""
        database = database
#
# class InternalUser(DBModel):
#     pass


class PdfCreation(DBModel):
    """The .pdf creation status table"""
    pdf_creation_id = pw.PrimaryKeyField()
    # user_id = pw.ForeignKeyField(InternalUser, null=True)
    datetime_ = pw.DateTimeField(index=True, default=datetime.datetime.now)
    request_raw = CompressedField(null=True, default=None)
    request_2nd_level = CompressedField(null=True, default=None)
    tex_raw = CompressedField(null=True, default=None)
    pdf_raw = CompressedField(null=True, default=None)
    pdf_signed = CompressedField(null=True, default=None)
    state = pw.SmallIntegerField(index=True, default=REQUEST_RAW)  # see state constants at the beginning of the file
    locked_timestamp = pw.DateTimeField(index=True, null=True, default=datetime.datetime(1980,1,1))

    @classmethod
    @database.atomic()
    def get_locked_task(self, required_state=None, task_timeout=TIMEOUT):
        """Gets the PdfCreation locked object with given state"""
        timeouted_task_time = datetime.datetime.now() - task_timeout
        task_query = PdfCreation.select().where((PdfCreation.locked_timestamp <= timeouted_task_time))
        if required_state is not None:  # if specified, filter along required_state!
            task_query = task_query.where(PdfCreation.state == required_state)
        try:
            task = task_query.get()
        except pw.DoesNotExist as _:
            return None  # if no task matches the query

        task.locked_timestamp = datetime.datetime.now()
        task.save()
        return task


def create_all_tables(fail_silently=True):
    # InternalUser.create_table(fail_silently=fail_silently)
    PdfCreation.create_table(fail_silently=fail_silently)
    print("ENSURED table existence!")


# ensure all the tables are created
create_all_tables()


if __name__ == '__main__':
    """Testing on commandline"""
    print(database.is_closed())
    create_all_tables()
    PdfCreation().save()
    obj = PdfCreation.get()
    print(obj)
    print(database.is_closed())
    database.close()
    print(database.is_closed())
    os.remove("my_database.db")
