from google.api_core.exceptions import Conflict, BadRequest
from google.cloud import storage
from omegaconf import OmegaConf

config = OmegaConf.load('config.yaml')


def init_raw_directories(bucket_name: str, dataset_type: str):  # inicializar_tipos_datasets_directorio
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    folder_name = dataset_type+'/'
    # Crea un blob que representa la carpeta
    blob = bucket.blob(folder_name)

    # Sube un contenido vacío para "crear" la carpeta
    blob.upload_from_string('')

    # return {"response": f'Raw directories initialized in bucket {bucket_name} for dataset type {dataset_type}'}


def create_bucket(bucket_name: str, members: list):
    try:
        storage_client = storage.Client()
        bucket = storage_client.create_bucket(bucket_name, location=config.gcp.location)

        policy = bucket.get_iam_policy(requested_policy_version=3)

        for member in members:
            print(f'Member: {member.strip(" ")} - Role: {config.storage.roles.bucket_level}')
            policy.bindings.append({"role": config.storage.roles.bucket_level,
                                    "members": [f'user:{member.strip(" ")}']})

        bucket.set_iam_policy(policy)

        return 'ok'
    except Conflict as e:
        return str(e)
    except BadRequest as e:
        return str(e)
