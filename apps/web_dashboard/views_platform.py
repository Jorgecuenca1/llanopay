from django.shortcuts import render


def platform_app(request):
    """Serve the user-facing SPA platform."""
    return render(request, 'platform/app.html')
