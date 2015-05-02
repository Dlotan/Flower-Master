from .factory import create_celery_app

celery = create_celery_app()


@celery.task
def async_bla():
    print("START")
    async_bla.apply_async(countdown=10)
