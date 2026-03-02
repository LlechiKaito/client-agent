from mangum import Mangum

from container.container import create_app

app = create_app()
handler = Mangum(app, lifespan="off")
