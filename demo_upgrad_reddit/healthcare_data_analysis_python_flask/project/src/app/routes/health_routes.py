from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint(
    "Health",
    "health",
    url_prefix="/health"
)

@blp.route("/")
class HealthResource(MethodView):
    @blp.response(200, None)
    @blp.doc(tags=["Monitoring", "HealthCheck"], summary="Liveness/readiness check endpoint.")
    def get(self):
        return {"status": "ok"}