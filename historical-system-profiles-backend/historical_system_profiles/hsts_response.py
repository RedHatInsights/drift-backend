def register_hsts_response(app):
    @app.after_request
    def ensure_hsts_response(response):
        """
        This method will insert HSTS header into all responses the server
        send to client
        """
        app.logger.debug("Including hsts header in response")

        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=63072000; includeSubDomains; preload"
        return response
