import datetime
import time

from hcloud import Client
from hcloud.images import Image
from hcloud.locations.domain import Location
from hcloud.server_types import ServerType
from linode_api4 import LinodeClient, Instance

from .utility import generate_password


class ServerModel:
    slug = ""
    ipv4 = ""
    ipv6 = ""
    password = ""
    username = ""


class Linode:

    def get_client(self, token):
        return LinodeClient(token.key)

    def re_image(self, image):
        os_fields = {
            'AlmaLinux 8': 'linode/almalinux8', 'AlmaLinux 9': 'linode/almalinux9',
            'Alpine 3.15': 'linode/alpine3.15', 'Alpine 3.16': 'linode/alpine3.16', 'Alpine 3.17': 'linode/alpine3.17',
            'Alpine 3.18': 'linode/alpine3.18', 'Arch Linux': 'linode/arch', 'CentOS 7': 'linode/centos7',
            'CentOS Stream 8': 'linode/centos-stream8', 'CentOS Stream 9': 'linode/centos-stream9',
            'Debian 10': 'linode/debian10', 'Debian 11': 'linode/debian11', 'Debian 12': 'linode/debian12',
            'Fedora 36': 'linode/fedora36', 'Fedora 37': 'linode/fedora37', 'Fedora 38': 'linode/fedora38',
            'Gentoo': 'linode/gentoo', 'Kali Linux': 'linode/kali',
            'openSUSE Leap 15.4': 'linode/opensuse15.4', 'openSUSE Leap 15.5': 'linode/opensuse15.5',
            'Rocky Linux 8': 'linode/rocky8', 'Rocky Linux 9': 'linode/rocky9',
            'Slackware 15.0': 'linode/slackware15.0', 'Slackware 14.1': 'linode/slackware14.1',
            'Ubuntu 20.04 LTS': 'linode/ubuntu20.04', 'Ubuntu 22.04 LTS': 'linode/ubuntu22.04',
            'Ubuntu 22.10': 'linode/ubuntu22.10', 'Ubuntu 23.04': 'linode/ubuntu23.04',
            'Ubuntu 23.10': 'linode/ubuntu23.10',

        }
        return os_fields.get(image, "linode/ubuntu20.04")

    def re_location(self, location):
        location_fields = {
            'Mumbai': 'ap-west', 'Toronto': 'ca-central', 'Sydney': 'ap-southeast', 'Washington': 'us-iad',
            'Chicago': 'us-ord', 'Paris': 'fr-par', 'Seattle': 'us-sea', 'Sao Paulo': 'br-gru',
            'Amsterdam': 'nl-ams', 'Stockholm': 'se-sto', 'Chennai': 'in-maa', 'Osaka': 'jp-osa',
            'Milan': 'it-mil', 'Miami': 'us-mia', 'Jakarta': 'id-cgk', 'Los Angeles': 'us-lax',
            'Dallas': 'us-central', 'Fremont': 'us-west', 'Atlanta': 'us-southeast', 'Newark': 'us-east',
            'London': 'eu-west', 'Singapore': 'ap-south', 'Frankfurt': 'eu-central', 'Madrid': 'es-mad'
        }
        return location_fields.get(location.title())

    def server_create(self, name, server_object, image_name, location):
        res = {"status": False}
        try:
            client = self.get_client(server_object.datacenter.token)
            password = generate_password()
            response = client.linode.instance_create(
                label=name,
                ltype=server_object.slug,
                region=self.re_location(location),
                image=self.re_image(image_name),
                root_pass=password
            )
            server = ServerModel()
            server.token = server_object.datacenter.token
            server.ipv4 = response.ipv4[0]
            server.ipv6 = response.ipv6
            server.password = password
            server.username = 'root'
            server.slug = str(response.id)
            res["status"] = True
            res["server"] = server
            return res
        except Exception:
            return res

    def server_reboot(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].reboot()
            res["status"] = True
            return res
        except Exception as e:
            print(e)
            return res

    def server_shutdown(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].shutdown()
            res["status"] = True
            return res
        except Exception:
            return res

    def server_power_on(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].boot()
            res["status"] = True
            return res
        except Exception:
            return res

    def server_power_off(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].shutdown()
            res["status"] = True
            return res
        except Exception:
            return res

    def server_change_password(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            password = generate_password()
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].reset_instance_root_password(root_password=password)
            res["status"] = True
            res["password"] = password
            return res
        except Exception as e:
            if str(e) == "400: Linode must be powered off in order to reset root password.; ":
                res["message"] = "ابتدا سرور را خاموش کنید و پس از 1 دقیقه مجدد درخواست را ارسال کنید"
            return res

    def server_delete(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            server[0].delete()
            res["status"] = True
            return res
        except Exception as e:
            res["error"] = str(e)
            return res

    def server_traffic(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.linode.instances(Instance.id == int(server_object.slug))
            traffic = server[0].transfer_year_month(datetime.datetime.now().year, datetime.datetime.now().month)
            res["outgoing_traffic"] = traffic.bytes_out or 0
            res["status"] = True
            return res
        except Exception:
            return res


class Hetzner:

    def get_client(self, token):
        return Client(token=token.key)

    def re_image(self, image):
        os_fields = {
            'CentOS Stream 8': 'centos-stream-8', 'CentOS Stream 9': 'centos-stream-9',
            'Ubuntu 20.04': 'ubuntu-20.04', 'Ubuntu 22.04': 'ubuntu-22.04', 'Debian 11': 'debian-11', 
            'Debian 12': 'debian-12', 'Fedora 37': 'fedora-37', 'Fedora 38': 'fedora-38', 
            'Rocky 8': 'rocky-8', 'Rocky 9': 'rocky-9', 'AlmaLinux 8': 'alma-8', 'AlmaLinux 9': 'alma-9'
        }
        return os_fields.get(image, "ubuntu-20.04")

    def re_location(self, location):
        location_fields = {
            'nuremberg': 'nbg1', 'falkenstein': 'fsn1', 'helsinki': 'hel1', 'ashburn': 'ash', 'hillsboro': 'hil'
        }
        return location_fields.get(location.lower())

    def server_create(self, name, server_object, image_name, location):
        res = {"status": False}
        try:
            client = self.get_client(server_object.datacenter.token)
            response = client.servers.create(
                name=name,
                server_type=ServerType(name=server_object.slug),
                image=Image(name=self.re_image(image_name)),
                location=Location(name=self.re_location(location))
            )
            server = ServerModel()
            server.token = server_object.datacenter.token
            server.ipv4 = response.server.public_net.ipv4.ip
            server.ipv6 = response.server.public_net.ipv6.ip
            server.password = response.root_password
            server.username = 'root'
            server.slug = str(response.server.id)
            res["status"] = True
            res["server"] = server
            return res
        except Exception as e:
            print(e)
            return res

    def server_reboot(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            client.servers.reboot(server)
            res["status"] = True
            return res
        except Exception:
            return res

    def server_shutdown(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            client.servers.shutdown(server)
            res["status"] = True
            return res
        except Exception:
            return res

    def server_power_on(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            client.servers.power_on(server)
            res["status"] = True
            return res
        except Exception:
            return res

    def server_power_off(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            client.servers.shutdown(server)
            res["status"] = True
            return res
        except Exception:
            return res

    def server_change_password(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            response = client.servers.reset_password(server)
            res["status"] = True
            res["password"] = response.root_password
            return res
        except Exception:
            return res

    def server_change_ip(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            if server.status != "off":
                res["message"] = "ابتدا سرور را خاموش کنید و سپس اقدام کنید"
                return res
            original_ip = None
            if server.public_net.ipv4:
                primary_ips = client.primary_ips.get_all()
                for primary_ip in primary_ips:
                    if primary_ip.ip == server.public_net.ipv4.ip:
                        primary_ip.unassign()
                        original_ip = primary_ip
                        time.sleep(3)
                        break
            name = str(server_object.slug) + "-" + generate_password()
            new_ip = client.primary_ips.create(
                type="ipv4", datacenter=None, assignee_id=server.id.real, name=name, auto_delete=True
            )
            if original_ip:
                client.primary_ips.delete(original_ip)
            res["status"] = True
            res["ip"] = new_ip.primary_ip.ip
            res["message"] = "عملیات با موفقیت انجام شد - سرور را روشن کنید تا بتوانید با آیپی جدید به آن متصل شوید"
            return res
        except Exception as e:
            print(e)
            return res

    def server_delete(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            client.servers.delete(server)
            res["status"] = True
            return res
        except Exception as e:
            res["error"] = str(e)
            return res

    def server_traffic(self, server_object):
        res = {"status": False}
        try:
            client = self.get_client(server_object.token)
            server = client.servers.get_by_id(int(server_object.slug))
            res["outgoing_traffic"] = server.outgoing_traffic or 0
            res["status"] = True
            return res
        except Exception:
            return res
