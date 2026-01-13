from rest_framework.throttling import SimpleRateThrottle

class PollCreateThrottle(SimpleRateThrottle):
    scope = "poll_create"

    def get_cache_key(self, request, view):
        return self.get_ident(request, view)