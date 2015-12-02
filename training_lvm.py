"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class training_lvm(ShutItModule):


	def build(self, shutit):
		# Some useful API calls for reference. See shutit's docs for more info and options:
		#
		# ISSUING BASH COMMANDS
		# shutit.send(send,expect=<default>) - Send a command, wait for expect (string or compiled regexp)
		#                                      to be seen before continuing. By default this is managed
		#                                      by ShutIt with shell prompts.
		# shutit.multisend(send,send_dict)   - Send a command, dict contains {expect1:response1,expect2:response2,...}
		# shutit.send_and_get_output(send)   - Returns the output of the sent command
		# shutit.send_and_match_output(send, matches)
		#                                    - Returns True if any lines in output match any of
		#                                      the regexp strings in the matches list
		# shutit.send_until(send,regexps)    - Send command over and over until one of the regexps seen in the output.
		# shutit.run_script(script)          - Run the passed-in string as a script
		# shutit.install(package)            - Install a package
		# shutit.remove(package)             - Remove a package
		# shutit.login(user='root', command='su -')
		#                                    - Log user in with given command, and set up prompt and expects.
		#                                      Use this if your env (or more specifically, prompt) changes at all,
		#                                      eg reboot, bash, ssh
		# shutit.logout(command='exit')      - Clean up from a login.
		#
		# COMMAND HELPER FUNCTIONS
		# shutit.add_to_bashrc(line)         - Add a line to bashrc
		# shutit.get_url(fname, locations)   - Get a file via url from locations specified in a list
		# shutit.get_ip_address()            - Returns the ip address of the target
		# shutit.command_available(command)  - Returns true if the command is available to run
		#
		# LOGGING AND DEBUG
		# shutit.log(msg,add_final_message=False) -
		#                                      Send a message to the log. add_final_message adds message to
		#                                      output at end of build
		# shutit.pause_point(msg='')         - Give control of the terminal to the user
		# shutit.step_through(msg='')        - Give control to the user and allow them to step through commands
		#
		# SENDING FILES/TEXT
		# shutit.send_file(path, contents)   - Send file to path on target with given contents as a string
		# shutit.send_host_file(path, hostfilepath)
		#                                    - Send file from host machine to path on the target
		# shutit.send_host_dir(path, hostfilepath)
		#                                    - Send directory and contents to path on the target
		# shutit.insert_text(text, fname, pattern)
		#                                    - Insert text into file fname after the first occurrence of
		#                                      regexp pattern.
		# shutit.delete_text(text, fname, pattern)
		#                                    - Delete text from file fname after the first occurrence of
		#                                      regexp pattern.
		# shutit.replace_text(text, fname, pattern)
		#                                    - Replace text from file fname after the first occurrence of
		#                                      regexp pattern.
		# ENVIRONMENT QUERYING
		# shutit.host_file_exists(filename, directory=False)
		#                                    - Returns True if file exists on host
		# shutit.file_exists(filename, directory=False)
		#                                    - Returns True if file exists on target
		# shutit.user_exists(user)           - Returns True if the user exists on the target
		# shutit.package_installed(package)  - Returns True if the package exists on the target
		# shutit.set_password(password, user='')
		#                                    - Set password for a given user on target
		#
		# USER INTERACTION
		# shutit.get_input(msg,default,valid[],boolean?,ispass?)
		#                                    - Get input from user and return output
		# shutit.fail(msg)                   - Fail the program and exit with status 1
		#
		vagrantfile = '''Vagrant.configure('2') do |config|
  config.ssh.forward_agent = true
  # For vagrant-cashier plugin, see: http://fgrehm.viewdocs.io/vagrant-cachier
  # config.cache.scope = :box
  # config.cache.auto_detect = true

  config.vm.define :centos65 do |machine|
    machine.vm.box = '/space/vagrant/centos/CentOS-7-x86_64-AtomicHost-Vagrant-VirtualBox-20150228_01.box'
    machine.vm.hostname = 'centos65'
    # Tweak accordingly, if needed.
    # machine.vm.network :private_network, ip: '172.16.1.10'
    # machine.vm.network 'forwarded_port', guest: 80, host: 8080
    done = false
    machine.vm.provider :virtualbox do |vb|
      if done == false
        done = true
        # Uncomment to set specific Virtual Machine name in VirtualBox.
        #vb.name = 'centos65'
        vb.customize ['modifyvm', :id, '--memory', '1024', '--cpus', '1', '--rtcuseutc', 'on', '--natdnshostresolver1', 'on', '--nictype1', 'virtio', '--nictype2', 'virtio' ]
        # Attach SATA AHCI controller, if needed.
        vb.customize ['storagectl', :id, '--name', 'SATA Controller', '--add', 'sata' ]
        vb.customize ['createhd', '--filename', 'centos65-disk1.vdi', '--size', 10*1024 ]
        vb.customize ['createhd', '--filename', 'centos65-disk2.vdi', '--size', 10*1024 ]
        vb.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', 'centos65-disk1.vdi']
        # Alternatively: SATA Controller
        vb.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', 'centos65-disk2.vdi']
      end
    end
    machine.vm.provision 'shell', inline: <<-EOS.gsub(/^\s+/,'')
      disk=1
      for l in b c d e ; do
        [ -e /dev/sd${l}1 ] && continue ;
        (echo o; echo n; echo p; echo 1; echo; echo; echo w) | sudo fdisk /dev/sd${l} > /dev/null 2>&1 || true
        yes | sudo mkfs.ext4 -q /dev/sd${l}1 > /dev/null 2>&1 || true
        sudo mkdir -p /mnt/#{machine.vm.hostname}-disk-${disk} > /dev/null 2>&1 || true
        sudo mount /dev/sd${l}1 /mnt/#{machine.vm.hostname}-disk-${disk} > /dev/null 2>&1 || true
        disk=$(( disk + 1 ))
      done
    EOS
  end
end
'''
		shutit.send('rm -rf /tmp/lvm_vm')
		shutit.send('mkdir -p /tmp/lvm_vm')
		shutit.send('cd /tmp/lvm_vm')
		shutit.send_file('/tmp/lvm_vm/Vagrantfile',vagrantfile)
		shutit.send('vagrant up')
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -',note='Become root (there is a problem logging in as admin with the vagrant user)')
		shutit.send('umount /dev/sda1')
		shutit.send('umount /dev/sdb1')
		shutit.send('umount /dev/sdc1')
		shutit.multisend('pvcreate /dev/sda1',{'ipe it':'y'})
		shutit.multisend('pvcreate /dev/sdb1',{'ipe it':'y'})
		shutit.multisend('pvcreate /dev/sdc1',{'ipe it':'y'})

# pvcreate
# pv

# vg

# creating a pool?
#lvcreate --thin root_vg/pool0 -V 4G -n varlibdocker # thin device (take up no space, in the pool in rootvg with virtual 4G and named varlibdocker). overprovisioning. watch the pool space

#lvcreate 'normal device'
#mkfs /dev/mapper/root_vg-varlibdocker

# thin provisioning from a pool lv

		shutit.pause_point()
		shutit.logout()
		shutit.logout()
		shutit.send('vagrant destroy -f')
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return training_lvm(
		'shutit.training_lvm.training_lvm.training_lvm', 237902401.00,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['tk.shutit.vagrant.vagrant.vagrant','shutit-library.virtualbox.virtualbox.virtualbox']
	)

