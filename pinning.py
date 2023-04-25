#!/usr/bin/env python3

# https://forum.qubes-os.org/t/17949

import asyncio
import subprocess

import qubesadmin
import qubesadmin.events

# i5-13600k (smt=off)
P_CORES = '0-5'
E_CORES = '6-13'

tag = 'performance'

def vcpu_pin(vm, cores):
    vm_name = [vm.name]
    if str(getattr(vm, 'virt_mode')) == 'hvm':
        vm_name.append(vm.name + '-dm')
    for qube in vm_name:
        cmd = ['xl', 'vcpu-pin', qube, 'all', cores]
        subprocess.run(cmd).check_returncode()

def pin_by_tag(vm, event, **kwargs):
    vm = app.domains[str(vm)]
    if event == f'domain-tag-add:{tag}' and vm.is_running():
        vcpu_pin(vm, P_CORES)
    elif event == f'domain-tag-delete:{tag}' and vm.is_running():
        vcpu_pin(vm, E_CORES)
    elif event == 'domain-start':
        if tag in list(vm.tags):
            vcpu_pin(vm, P_CORES)
        else:
            vcpu_pin(vm, E_CORES)
    else:
        pass

app = qubesadmin.Qubes()
dispatcher = qubesadmin.events.EventsDispatcher(app)
dispatcher.add_handler('domain-start', pin_by_tag)
dispatcher.add_handler(f'domain-tag-add:{tag}', pin_by_tag)
dispatcher.add_handler(f'domain-tag-delete:{tag}', pin_by_tag)
asyncio.run(dispatcher.listen_for_events())
