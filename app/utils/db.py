import uuid

import pg8000.dbapi
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from omegaconf import OmegaConf
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from utils.db_models import UC, DatasetType, DatasetRaw, AdminUser


config = OmegaConf.load('config.yaml')


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.
    Uses the Cloud SQL Python Connector package.
    """
    connector = Connector(IPTypes.PUBLIC)

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            config.db.instance_connection_name,
            "pg8000",
            user=config.db.user,
            password=config.db.password,
            db=config.db.name
        )
        # conn.cursor().execute("SET SCHEMA 'divec'")
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn
    )

    return engine


class DB(object):
    db_config = ''
    engine = object

    def __init__(self) -> None:
        engine = connect_with_connector()

        Session = sessionmaker(bind=engine, future=True)
        self.session = Session()
        self.config = config

    def init_dataset_types(self, item: DatasetType):  # inicializar_tipos_datasets_catalogo
        try:
            print(f'DATASET TYPES: {item.nombre}')
            id_tipo_dataset = uuid.uuid4()
            item.id_tipo_dataset = id_tipo_dataset
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            print(e)
        finally:
            self.session.close()

        return {"response": "success"}

    def get_dataset_type(self, dataset_type: str):  # obtener_parametros_bbd
        # print(sqlalchemy.text(f"SELECT parametros from divec.tipos_datasets where id_tipo_dataset='{type}'"))

        try:
            dataset_metadata = self.session.execute(
                select(
                    DatasetType
                ).where(
                    DatasetType.nombre == dataset_type
                )
            ).scalar_one_or_none()

        except Exception as e:
            print(e)
            print(dataset_type)

        return dataset_metadata

    def insert_data_raw(self, item: DatasetRaw):

        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            print(e)
        finally:
            self.session.close()

        return 'ok'

    def init_uc(self, item: UC):  # update_uc

        try:
            print(f'UC: {item.descripcion} - {item.lider} - {item.responsables}')
            id_caso_uso = uuid.uuid4()
            item.id_caso_uso = id_caso_uso
            self.session.add(item)
            self.session.commit()

        except Exception as e:
            print(e)
            return None
        finally:
            self.session.close()

        return id_caso_uso

    def get_admin_users(self):
        admin_users_email_list = []
        try:
            admin_users = self.session.execute(
                select(
                    AdminUser
                )
            ).scalars()

            if admin_users is not None:
                for user in admin_users:
                    admin_users_email_list.append(user.email)

        except Exception as e:
            print(e)
        return admin_users_email_list
