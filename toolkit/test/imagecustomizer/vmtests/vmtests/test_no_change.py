import os
from getpass import getuser
from pathlib import Path
from typing import List, Tuple

import libvirt  # type: ignore
from docker import DockerClient

from .conftest import TEST_CONFIGS_DIR, Closeable
from .utils import local_client
from .utils.imagecustomizer import run_image_customizer
from .utils.libvirt_utils import VmSpec, create_libvirt_domain_xml
from .utils.libvirt_vm import LibvirtVm
from .utils.ssh_client import SshClient


def test_no_change(
    docker_client: DockerClient,
    image_customizer_container_url: str,
    core_efi_azl2: Path,
    ssh_key: Tuple[str, Path],
    test_temp_dir: Path,
    test_instance_name: str,
    libvirt_conn: libvirt.virConnect,
    close_list: List[Closeable],
) -> None:
    (ssh_public_key, ssh_private_key_path) = ssh_key

    config_path = TEST_CONFIGS_DIR.joinpath("nochange-config.yaml")
    output_image_path = test_temp_dir.joinpath("image.qcow2")
    diff_image_path = test_temp_dir.joinpath("image-diff.qcow2")

    username = getuser()

    run_image_customizer(
        docker_client,
        image_customizer_container_url,
        core_efi_azl2,
        config_path,
        username,
        ssh_public_key,
        "qcow2",
        output_image_path,
    )

    # Create a differencing disk for the VM.
    # This will make it easier to manually debug what is in the image itself and what was set during first boot.
    local_client.run(
        ["qemu-img", "create", "-F", "qcow2", "-f", "qcow2", "-b", str(output_image_path), str(diff_image_path)],
    ).check_exit_code()

    # Ensure VM can write to the disk file.
    os.chmod(diff_image_path, 0o666)

    # Create VM.
    vm_name = test_instance_name
    domain_xml = create_libvirt_domain_xml(VmSpec(vm_name, 4096, 4, diff_image_path))

    vm = LibvirtVm(vm_name, domain_xml, libvirt_conn)
    close_list.append(vm)

    # Start VM.
    vm.start()

    vm_ip_address = vm.get_vm_ip_address(timeout=15)

    # Connect to VM using SSH.
    ssh_known_hosts_path = test_temp_dir.joinpath("known_hosts")
    open(ssh_known_hosts_path, "w").close()

    with SshClient(vm_ip_address, key_path=ssh_private_key_path, known_hosts_path=ssh_known_hosts_path) as vm_ssh:
        vm_ssh.run("cat /etc/os-release").check_exit_code()
