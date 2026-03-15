import docker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import json


def index(request):
    """Serve the main HTML page."""
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def launch_lab(request):
    """
    Launch a new Docker container for the user session.
    Returns the container ID so frontend can open WebSocket.
    """
    try:
        client = docker.from_env()

        try:
            client.images.get('ubuntu:latest')
        except docker.errors.ImageNotFound:
            client.images.pull('ubuntu:latest')

        container = client.containers.run(
            'ubuntu:latest',
            '/bin/bash',
            detach=True,          # run in background
            tty=True,             # allocate pseudo-TTY (needed for interactive terminal)
            stdin_open=True,      # keep stdin open (needed for input)
            auto_remove=False,    # we'll manually remove on disconnect
            mem_limit='256m',     # max 256MB RAM per container
            cpu_period=100000,
            cpu_quota=50000,      # max 50% of one CPU core
        )

        return JsonResponse({
            'status': 'success',
            'container_id': container.id,
            'container_short_id': container.short_id,
        })

    except docker.errors.DockerException as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Docker error: {str(e)}'
        }, status=500)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stop_lab(request):
    """Stop and remove a container when user ends the lab."""
    try:
        data = json.loads(request.body)
        container_id = data.get('container_id')

        if not container_id:
            return JsonResponse({'status': 'error', 'message': 'No container_id'}, status=400)

        client = docker.from_env()
        try:
            container = client.containers.get(container_id)
            container.stop(timeout=3)
            container.remove()
        except docker.errors.NotFound:
            pass  # Already removed

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def container_status(request, container_id):
    """Get the current status of a container."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        return JsonResponse({
            'status': 'success',
            'container_status': container.status,
            'container_id': container.short_id,
        })
    except docker.errors.NotFound:
        return JsonResponse({'status': 'success', 'container_status': 'removed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_lab(request):
    """Stop existing container and create a fresh one."""
    try:
        data = json.loads(request.body)
        old_container_id = data.get('container_id')

        client = docker.from_env()

        if old_container_id:
            try:
                old = client.containers.get(old_container_id)
                old.stop(timeout=3)
                old.remove()
            except docker.errors.NotFound:
                pass

        container = client.containers.run(
            'ubuntu:latest',
            '/bin/bash',
            detach=True,
            tty=True,
            stdin_open=True,
            auto_remove=False,
            mem_limit='256m',
            cpu_period=100000,
            cpu_quota=50000,
        )

        return JsonResponse({
            'status': 'success',
            'container_id': container.id,
            'container_short_id': container.short_id,
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)