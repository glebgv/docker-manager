#!/usr/bin/env python3
"""
Docker Manager Pro - Python Flask Backend
API Server для управления Docker контейнерами
"""

import os
import json
import logging
from datetime import datetime, timezone
from dateutil.parser import isoparse
from flask import Flask, jsonify, request
from flask_cors import CORS
import docker
from docker.errors import DockerException, NotFound

# === КОНФИГУРАЦИЯ ===
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Docker клиент с поддержкой различных платформ
docker_client = None
DOCKER_AVAILABLE = False

def init_docker():
    """Инициализировать Docker клиент с поддержкой разных платформ"""
    global docker_client, DOCKER_AVAILABLE

    docker_hosts = [
        None,  # Стандартное подключение
        'unix:///var/run/docker.sock',  # Linux
        'unix:///run/docker.sock',  # Альтернативный Linux путь
        'unix:///Users/.docker/run/docker.sock',  # Mac
        'tcp://127.0.0.1:2375',  # TCP подключение
    ]

    # Если есть переменная окружения
    if 'DOCKER_HOST' in os.environ:
        docker_hosts.insert(0, os.environ['DOCKER_HOST'])

    for docker_host in docker_hosts:
        try:
            if docker_host:
                logger.info(f"🔄 Попытка подключения к: {docker_host}")
                docker_client = docker.DockerClient(base_url=docker_host)
            else:
                logger.info("🔄 Попытка стандартного подключения к Docker...")
                docker_client = docker.from_env()

            # Проверить соединение
            docker_client.ping()
            DOCKER_AVAILABLE = True

            version = docker_client.version().get('Version', 'unknown')
            logger.info(f"✅ Docker подключен успешно (версия {version})")

            if docker_host:
                logger.info(f"   📍 Используется: {docker_host}")

            return

        except Exception as e:
            if docker_host:
                logger.debug(f"   ❌ Не удалось подключиться к {docker_host}: {e}")
            else:
                logger.debug(f"   ❌ Стандартное подключение не работает: {e}")
            continue

    # Если ничего не сработало
    DOCKER_AVAILABLE = False
    logger.warning("⚠️  Docker недоступен ни через один способ подключения")
    logger.warning("")
    logger.warning("💡 Решения:")
    logger.warning("")
    logger.warning("Для WSL2/Linux:")
    logger.warning("  1. Убедитесь, что Docker запущен:")
    logger.warning("     sudo systemctl start docker")
    logger.warning("  2. Добавьте себя в группу docker:")
    logger.warning("     sudo usermod -aG docker $USER")
    logger.warning("  3. Перезагрузитесь или выполните:")
    logger.warning("     newgrp docker")
    logger.warning("")
    logger.warning("Для Windows (Docker Desktop):")
    logger.warning("  1. Откройте Docker Desktop приложение")
    logger.warning("  2. Включите интеграцию с WSL2 в Settings")
    logger.warning("")
    logger.warning("Для Mac:")
    logger.warning("  1. Откройте Docker Desktop приложение")
    logger.warning("")

# Инициализировать Docker при запуске
init_docker()

# === HELPERS ===
def get_docker_info():
    """Получить информацию о Docker"""
    if not DOCKER_AVAILABLE:
        return {
            'status': 'unavailable',
            'message': 'Docker не подключен',
            'suggestion': 'Проверьте установку и запуск Docker'
        }

    try:
        info = docker_client.info()
        return {
            'status': 'ok',
            'version': docker_client.version().get('Version', 'unknown'),
            'containers_total': info.get('Containers', 0),
            'containers_running': info.get('ContainersRunning', 0),
            'containers_paused': info.get('ContainersPaused', 0),
            'containers_stopped': info.get('Containers', 0) - info.get('ContainersRunning', 0),
            'images': info.get('Images', 0),
            'kernel': info.get('KernelVersion', 'unknown'),
            'os': info.get('OperatingSystem', 'unknown'),
        }
    except Exception as e:
        logger.error(f"Error getting Docker info: {e}")
        return {'status': 'error', 'message': str(e)}

def format_container(container):
    """Форматировать данные контейнера"""
    try:
        try:
            stats = container.stats(stream=False)
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0

            memory_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)
        except Exception:
            cpu_percent = 0
            memory_usage = 0

        # Правильный расчёт uptime
        uptime = 0
        started_at_str = container.attrs.get('State', {}).get('StartedAt', '')
        if started_at_str and container.status == 'running':
            try:
                # StartedAt — строка вроде "2026-01-16T13:49:03.123456789Z"
                started_at = isoparse(started_at_str)
                now = datetime.now(timezone.utc) if started_at.tzinfo is None else datetime.now(started_at.tzinfo)
                uptime = (now - started_at).total_seconds()
            except Exception as parse_error:
                logger.error(f"Error parsing StartedAt '{started_at_str}': {parse_error}")
                uptime = 0

        return {
            'id': container.id[:12],
            'name': container.name,
            'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
            'status': container.status,
            'state': container.attrs.get('State', {}),
            'ports': container.ports or {},
            'cpu_percent': round(cpu_percent, 2),
            'memory_mb': round(memory_usage, 2),
            'created': container.attrs.get('Created', ''),
            'uptime': round(uptime, 2),
        }
    except Exception as e:
        logger.error(f"Error formatting container: {e}")
        return {
            'id': container.id[:12],
            'name': container.name,
            'image': 'unknown',
            'status': 'unknown',
            'error': str(e)
        }

# === HEALTH CHECK ===
@app.route('/api/health', methods=['GET'])
def health():
    """Проверка здоровья сервера"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'docker': 'connected' if DOCKER_AVAILABLE else 'disconnected',
        'version': '1.0.0'
    })

# === CONTAINERS API ===
@app.route('/api/containers', methods=['GET'])
def list_containers():
    """Получить список всех контейнеров"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available', 'message': 'Запустите Docker'}), 503

    try:
        containers = docker_client.containers.list(all=True)
        result = [format_container(c) for c in containers]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>', methods=['GET'])
def get_container(container_id):
    """Получить детали контейнера"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        return jsonify(format_container(container))
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error getting container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers', methods=['POST'])
def create_container():
    """Создать новый контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        data = request.get_json()
        image = data.get('image')
        name = data.get('name')

        if not image or not name:
            return jsonify({'error': 'Image and name are required'}), 400

        ports = {}
        port_bindings = {}
        if data.get('ports'):
            for port in data.get('ports', []):
                container_port = port.get('container_port')
                host_port = port.get('host_port')
                ports[f'{container_port}/tcp'] = None
                port_bindings[f'{container_port}/tcp'] = host_port

        container = docker_client.containers.create(
            image,
            name=name,
            environment=data.get('env', []),
            ports=ports if ports else None,
            host_config=docker_client.api.create_host_config(
                port_bindings=port_bindings if port_bindings else None
            )
        )

        return jsonify({'id': container.id[:12], 'status': 'created'}), 201
    except Exception as e:
        logger.error(f"Error creating container: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/containers/<container_id>/start', methods=['POST'])
def start_container(container_id):
    """Запустить контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        container.start()
        logger.info(f"Container {container_id} started")
        return jsonify({'status': 'started'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error starting container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>/stop', methods=['POST'])
def stop_container(container_id):
    """Остановить контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        logger.info(f"Container {container_id} stopped")
        return jsonify({'status': 'stopped'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error stopping container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>/restart', methods=['POST'])
def restart_container(container_id):
    """Перезагрузить контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        container.restart()
        logger.info(f"Container {container_id} restarted")
        return jsonify({'status': 'restarted'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error restarting container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>/pause', methods=['POST'])
def pause_container(container_id):
    """Пауза контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        container.pause()
        logger.info(f"Container {container_id} paused")
        return jsonify({'status': 'paused'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error pausing container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>/unpause', methods=['POST'])
def unpause_container(container_id):
    """Возобновить контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        container.unpause()
        logger.info(f"Container {container_id} unpaused")
        return jsonify({'status': 'unpaused'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error unpausing container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>/logs', methods=['GET'])
def get_logs(container_id):
    """Получить логи контейнера"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        lines = request.args.get('lines', 50, type=int)
        logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
        return jsonify({'logs': logs})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error getting logs for {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    """Удалить контейнер"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        container = docker_client.containers.get(container_id)
        force = request.args.get('force', 'false').lower() == 'true'
        container.remove(force=force)
        logger.info(f"Container {container_id} deleted")
        return jsonify({'status': 'deleted'})
    except NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting container {container_id}: {e}")
        return jsonify({'error': str(e)}), 500

# === IMAGES API ===
@app.route('/api/images', methods=['GET'])
def list_images():
    """Получить список всех образов"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        images = docker_client.images.list()
        result = []
        for img in images:
            result.append({
                'id': img.id[:12],
                'tags': img.tags or ['<none>'],
                'size': img.attrs.get('Size', 0) / (1024 * 1024),
                'created': img.attrs.get('Created', ''),
            })
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/pull', methods=['POST'])
def pull_image():
    """Скачать образ"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        data = request.get_json()
        image_name = data.get('image')

        if not image_name:
            return jsonify({'error': 'Image name is required'}), 400

        logger.info(f"Pulling image: {image_name}")
        docker_client.images.pull(image_name)
        logger.info(f"Image pulled: {image_name}")
        return jsonify({'status': 'pulled', 'image': image_name}), 201
    except Exception as e:
        logger.error(f"Error pulling image: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/images/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Удалить образ"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        force = request.args.get('force', 'false').lower() == 'true'
        docker_client.images.remove(image_id, force=force)
        logger.info(f"Image {image_id} deleted")
        return jsonify({'status': 'deleted'})
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {e}")
        return jsonify({'error': str(e)}), 500

# === NETWORKS API ===
@app.route('/api/networks', methods=['GET'])
def list_networks():
    """Получить список всех сетей"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        networks = docker_client.networks.list()
        result = []
        for net in networks:
            result.append({
                'id': net.id[:12],
                'name': net.name,
                'driver': net.attrs.get('Driver', 'bridge'),
                'containers': len(net.containers),
                'created': net.attrs.get('Created', ''),
            })
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing networks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/networks/<network_id>', methods=['GET'])
def get_network(network_id):
    """Получить детали сети"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        network = docker_client.networks.get(network_id)
        return jsonify({
            'id': network.id[:12],
            'name': network.name,
            'driver': network.attrs.get('Driver', 'bridge'),
            'containers': list(network.containers),
            'created': network.attrs.get('Created', ''),
        })
    except Exception as e:
        logger.error(f"Error getting network {network_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/networks', methods=['POST'])
def create_network():
    """Создать сеть"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        data = request.get_json()
        name = data.get('name')
        driver = data.get('driver', 'bridge')

        if not name:
            return jsonify({'error': 'Name is required'}), 400

        network = docker_client.networks.create(name, driver=driver)
        logger.info(f"Network {name} created")
        return jsonify({'id': network.id[:12], 'name': network.name}), 201
    except Exception as e:
        logger.error(f"Error creating network: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/networks/<network_id>', methods=['DELETE'])
def delete_network(network_id):
    """Удалить сеть"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        network = docker_client.networks.get(network_id)
        network.remove()
        logger.info(f"Network {network_id} deleted")
        return jsonify({'status': 'deleted'})
    except Exception as e:
        logger.error(f"Error deleting network {network_id}: {e}")
        return jsonify({'error': str(e)}), 500

# === VOLUMES API ===
@app.route('/api/volumes', methods=['GET'])
def list_volumes():
    """Получить список всех томов"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        volumes = docker_client.volumes.list()
        result = []
        for vol in volumes:
            result.append({
                'name': vol.name,
                'driver': vol.attrs.get('Driver', 'local'),
                'mountpoint': vol.attrs.get('Mountpoint', ''),
                'created': vol.attrs.get('CreatedAt', ''),
            })
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing volumes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/volumes/<volume_name>', methods=['GET'])
def get_volume(volume_name):
    """Получить детали тома"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        volume = docker_client.volumes.get(volume_name)
        return jsonify({
            'name': volume.name,
            'driver': volume.attrs.get('Driver', 'local'),
            'mountpoint': volume.attrs.get('Mountpoint', ''),
            'labels': volume.attrs.get('Labels', {}),
            'created': volume.attrs.get('CreatedAt', ''),
        })
    except Exception as e:
        logger.error(f"Error getting volume {volume_name}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/volumes', methods=['POST'])
def create_volume():
    """Создать том"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        data = request.get_json()
        name = data.get('name')
        driver = data.get('driver', 'local')

        if not name:
            return jsonify({'error': 'Name is required'}), 400

        volume = docker_client.volumes.create(name, driver=driver)
        logger.info(f"Volume {name} created")
        return jsonify({'name': volume.name, 'driver': volume.attrs.get('Driver', 'local')}), 201
    except Exception as e:
        logger.error(f"Error creating volume: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/volumes/<volume_name>', methods=['DELETE'])
def delete_volume(volume_name):
    """Удалить том"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        volume = docker_client.volumes.get(volume_name)
        volume.remove()
        logger.info(f"Volume {volume_name} deleted")
        return jsonify({'status': 'deleted'})
    except Exception as e:
        logger.error(f"Error deleting volume {volume_name}: {e}")
        return jsonify({'error': str(e)}), 500

# === SYSTEM API ===
@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Получить информацию о системе"""
    try:
        docker_info = get_docker_info()
        return jsonify(docker_info)
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/prune', methods=['POST'])
def system_prune():
    """Очистить неиспользуемые ресурсы"""
    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker not available'}), 503

    try:
        result = docker_client.containers.prune()
        logger.info(f"System pruned: {len(result.get('ContainersDeleted', []))} containers deleted")
        return jsonify({
            'status': 'pruned',
            'containers_deleted': len(result.get('ContainersDeleted', [])),
            'space_reclaimed': result.get('SpaceReclaimed', 0),
        })
    except Exception as e:
        logger.error(f"Error pruning system: {e}")
        return jsonify({'error': str(e)}), 500

# === FRONTEND ===
@app.route('/')
def serve_frontend():
    """Служить фронтенд"""
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def catch_all(path):
    """Перенаправить все маршруты на index.html для Single Page Application"""
    return app.send_static_file('index.html')

# === ERROR HANDLERS ===
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# === RUN ===
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info("=" * 70)
    logger.info("🐳 Docker Manager Pro v1.0.0")
    logger.info("=" * 70)
    logger.info(f"🌐 Запуск сервера на http://0.0.0.0:{port}")
    logger.info(f"🔍 Docker статус: {'✅ подключен' if DOCKER_AVAILABLE else '⚠️  недоступен'}")

    if not DOCKER_AVAILABLE:
        logger.warning("")
        logger.warning("⚠️  ПРЕДУПРЕЖДЕНИЕ: Docker недоступен!")
        logger.warning("")
        logger.warning("Убедитесь, что:")
        logger.warning("  1. Docker установлен[](https://www.docker.com/products/docker-desktop)")
        logger.warning("  2. Docker запущен:")
        logger.warning("     - Windows/Mac: откройте Docker Desktop приложение")
        logger.warning("     - Linux: запустите 'sudo systemctl start docker'")
        logger.warning("     - WSL: запустите 'sudo service docker start'")
        logger.warning("  3. Проверьте доступ: 'docker ps'")
        logger.warning("")
        logger.warning("Сервер всё равно запущен, но без Docker функциональности!")
        logger.warning("")

    logger.info("=" * 70)
    logger.info(f"📖 Документация API: http://localhost:{port}/api/health")
    logger.info("=" * 70)
    logger.info("")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
