import uuid
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from google.cloud import storage
from omegaconf import OmegaConf
from pydantic.v1 import parse_raw_as

import utils.db as db
import utils.db_models as db_models
import utils.pydantic_models as p_models
import utils.storage as storage_functions

dbSQL = db.DB()

config = OmegaConf.load('config.yaml')

app = FastAPI(title='DIVEC - Data Management API')


@app.post("/datasets/types")
async def init_dataset_types(dataset_conf: List[p_models.DatasetType]):
    # Creamos el bucket de datos raw si no existe
    storage_client = storage.Client()
    bucket = storage_client.lookup_bucket(config.storage.buckets.raw)
    if bucket is None:
        raw_bucket_members = dbSQL.get_admin_users()
        response = storage_functions.create_bucket(config.storage.buckets.raw, raw_bucket_members)
        if response != 'ok':
            raise HTTPException(status_code=500, detail=response)

    # Inicializamos los directorios de datasets en el bucket
    for item in dataset_conf:
        dbSQL.init_dataset_types(db_models.DatasetType.from_pydantic(item))

        storage_functions.init_raw_directories(config.storage.buckets.raw, item.nombre)

    return {"response": f'Tipos de dataset inicializados'}


@app.post("/datasets")
async def upload_raw_dataset(file: UploadFile = File(...), dataset_metadata: str = Form()):
    dataset_metadata = parse_raw_as(p_models.FileMetadata, dataset_metadata)
    dataset_type_name = dataset_metadata.tipo_dataset

    dataset_type = dbSQL.get_dataset_type(dataset_type_name)

    if sorted(dataset_type.parametros.keys()) != sorted(dataset_metadata.parametros.keys()):
        raise HTTPException(status_code=422,
                            detail=f'Los parámetros enviados no coinciden con los del tipo {dataset_type}')

    file_name_in = f'{uuid.uuid4()}.{file.filename.split(".")[1]}'
    ruta = f'{dataset_metadata.tipo_dataset}/{file_name_in}'
    dataset_dbobject = db_models.DatasetRaw(
        nombre=file.filename,
        id_tipo_dataset=dataset_type.id_tipo_dataset,
        ruta=f'{config.storage.buckets.raw}/{ruta}',
        owner=dataset_metadata.owner,
        parametros=dataset_metadata.parametros
    )
    dbSQL.insert_data_raw(dataset_dbobject)

    storage_client = storage.Client()
    bucket = storage_client.lookup_bucket(config.storage.buckets.raw)

    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")

    bucket = storage_client.bucket(config.storage.buckets.raw)

    blob = bucket.blob(ruta)
    blob.upload_from_string(data=await file.read())

    return {"result": f'File uploaded to this path: {config.storage.buckets.raw}/{ruta}'}


@app.post("/uc")
async def init_uc(uc_metadata: List[p_models.UC]):
    response_msg = None
    for item in uc_metadata:
        if len(item.responsables) == 0:
            item.responsables = dbSQL.get_admin_users()

        id_caso_uso = dbSQL.init_uc(db_models.UC.from_pydantic(item))
        if id_caso_uso is None:
            response_msg = id_caso_uso
            break

        response = storage_functions.create_bucket(str(id_caso_uso), item.responsables)
        if response != 'ok':
            response_msg = response
            break

    if response_msg is None:
        return {"result": "Casos de uso inicializados"}
    else:
        raise HTTPException(status_code=500, detail=response_msg)
