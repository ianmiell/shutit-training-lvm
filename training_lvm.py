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
		shutit.send('rm -rf /tmp/lvm_vm')
		shutit.send('mkdir -p /tmp/lvm_vm')
		shutit.send('cd /tmp/lvm_vm')
		shutit.send('vagrant init ianmiell/centos7_lvm')
		shutit.send('vagrant up --provider virtualbox')
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -')
		#cf https://docs.docker.com/engine/userguide/storagedriver/device-mapper-driver/
		# https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Logical_Volume_Manager_Administration/thinly_provisioned_volume_creation.html
		shutit.send('ls /dev/sd*',note='List the available disks. We have 4 drives that are un-mounted and un-partitioned - sda,sdb,...')
		shutit.send('pvdisplay',note='Now show the physical volumes (the lowest layer of lvm) we have in our volume management. pv/vg/lvdisplay are good default commands to run when you are stuck.')
		shutit.send('pvcreate /dev/sdb',note='Use pbcreate to give sdb to the physical volume (pv) manager to manage.')
		shutit.send('pvscan',note='Use pvscan to scan disks for physical volumes. sdb is not assigned to a volume group, whereas the sda5 partition is assigned to the vagrant volume group.')
		shutit.send('pvdisplay',note='Display the current status in longer form')
		# new volume group
		shutit.send('vgcreate newvg1 /dev/sdb',note='Create a new volume group (the next level up in the hierarchy), giving it the sdb physical disk to manage.')
		shutit.send('vgdisplay newvg1',note='newvg1 has been added to the volume groups')
		shutit.send('lvcreate -L +100M -n newvol1 newvg1',note='Create a logical volume (logical volumes are at the top of the lvm hierarchy) within this new volume group')
		shutit.send('lvcreate -l +100%FREE -n newvol2 newvg1',note='Allocate any remaining free space to another volume using the 100%FREE specifier. Note this is -l, not -L.')
		shutit.send('vgdisplay newvg1',note='Show the new state of the volume group we have created.')
		shutit.send('lvremove /dev/mapper/newvg1-newvol1',{'really':'y'},note='Remove the smaller logical volume we just created')
		shutit.send('lvremove /dev/mapper/newvg1-newvol2',{'really':'y'},note='Remove the larger logical volume we just created')

		## Breaks filesystem! http://man7.org/linux/man-pages/man7/lvmthin.7.html, lvconvert --repair VG/ThinPoolLV?
		### create thin pool - man lvmthin
		## https://lxadm.wordpress.com/2012/10/17/lvm-thin-provisioning/ - appears to be a bug!?
		#shutit.send('lvcreate -L 1G -T newvg1/newthinpool',note='Create a thin pool of size 1 Gigabyte.')
		#shutit.send('lvcreate --thin newvg1/newthinpool -V 100M -n virtualvol1',note='Create a thin device within that pool (takes up no space, in the pool in rootvg with virtual 100M and named virtualvol1).')
		#shutit.send('lvcreate --thin newvg1/newthinpool -V 2G -n virtualvol2',note='Create another thin device within that pool.\n\nNotice how we overprovision this pool with two pools adding up to ~2.1G for a 1G thin volume.')
		## mount
		#shutit.send('mkdir /mnt/thinvol2_dir',note='Make a directory to mount that volume onto')
		#shutit.send('mkfs.ext4 /dev/mapper/newvg1-virtualvol2',note='Set up the filesystem for the thin pool')
		#shutit.send('mount -t auto /dev/mapper/newvg1-virtualvol2 /mnt/thinvol2_dir',note='Mount the thin volume onto the mount point we created.')
		## overfill
		#shutit.send('dd if=/dev/urandom of=/mnt/thinvol2_dir/afile bs=1M count=1500',note='Now we will try and overfill this thin volume with ~1.5GiB, which is less than the virtual size of 2GiB, but more than the physical space allocated to the thin pool it was placed in (1GiB)')
		## dmesg errors, the file did not get actually written! Is this a bug?

		## create safer thin pool
		shutit.send('lvcreate -L 1.95G -T newvg1/newthinpool',note='Create a thin pool of size 1 Gigabyte. A thin pool can have thinly-provisioned volumes placed in it. Thinly-provisioned volumes are given a virtual size, and take up no "real" space until you put data in them.')
		shutit.send('lvcreate --thin newvg1/newthinpool -V 100M -n virtualvol1',note='Create a thin device within that pool (takes up no space, in the pool in rootvg with virtual 100M and named virtualvol1).')
		shutit.send('lvcreate --thin newvg1/newthinpool -V 1G -n virtualvol2',note='Create another thin device within that pool.')
		## mount
		shutit.send('mkdir /mnt/thinvol2_dir',note='Make a directory to mount that volume onto')
		shutit.send('mkfs.ext4 /dev/mapper/newvg1-virtualvol2',note='Set up the filesystem for the thin pool')
		shutit.send('mount -t auto /dev/mapper/newvg1-virtualvol2 /mnt/thinvol2_dir',note='Mount the thin volume onto the mount point we created.')
		## overfill
		shutit.send('dd if=/dev/urandom of=/mnt/thinvol2_dir/afile bs=1M count=1100',note='Now we will try and overfill this thin volume with ~1.1GiB, which is more than the virtual size of 1GiB, but less than the physical space allocated to the thin pool it was placed in (1.5GiB). It should fail.',check_exit=False)
		shutit.send('rm -f /mnt/thinvol2_dir/afile',note='Remove the file.')
		# resizing: http://blog.intelligencecomputing.io/infra/12040/repost-lvm-resizing-guide
		shutit.send('lvresize -L +0.4G newvg1/virtualvol2',note='resize the logical volume to add 0.4G to it')
		shutit.send('df -kh /dev/mapper/newvg1-virtualvol2',note='Even though we have resized the logical volume, the filesystem (df) still gives us the same size as previously ~1G.')
		shutit.send('resize2fs /dev/mapper/newvg1-virtualvol2',note='Resize the filesystem to reflect the new size of the logical volume. You could also add -r/--resize to the lvresize command.')
		shutit.send('df -kh /dev/mapper/newvg1-virtualvol2',note='The size of the logical volume is now reflected in the filesystem')
		shutit.send('dd if=/dev/urandom of=/mnt/thinvol2_dir/afile bs=1M count=1100',note='Now the file creation should work.')
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

