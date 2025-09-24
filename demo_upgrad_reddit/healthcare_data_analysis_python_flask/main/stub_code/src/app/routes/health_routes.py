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
        # TODO: Implement logic to return health check status as a dictionary (e.g., {"status": "ok"})
        pass