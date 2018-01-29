# See also: https://docs.docker.com/engine/userguide/storagedriver/device-mapper-driver/
from shutit_module import ShutItModule


class training_lvm(ShutItModule):

	def build(self, shutit):
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
		shutit.send('lvcreate -l +80%FREE -n newvol2 newvg1',note='Allocate any remaining free space to another volume using the 100%FREE specifier. Note this is -l, not -L.')
		shutit.send('vgdisplay newvg1',note='Show the new state of the volume group we have created.')

		shutit.send('mkdir /mnt/newvol1_dir',note='Make a directory to mount that volume onto')
		shutit.send('mkfs.ext4 /dev/mapper/newvg1-newvol1',note='Set up the filesystem for the thin pool')
		shutit.send('mount -t auto /dev/mapper/newvg1-newvol1 /mnt/newvol1_dir',note='Mount the thin volume onto the mount point we created.')
		shutit.send('dd if=/dev/urandom of=/mnt/newvol1_dir/afile bs=1M count=1',note='Create a file in the volume ready to snapshot',check_exit=False)
		shutit.send('lvcreate -s -L 10M -n newvol1snap newvg1/newvol1',note='Create a snapshot with 10M space of newvol1')
		shutit.send('lvs',note='New snapshot is there')

		shutit.send('lvremove /dev/mapper/newvg1-newvol1',{'really':'y'},note='Remove the smaller logical volume we just created')
		shutit.send('lvremove /dev/mapper/newvg1-newvol2',{'really':'y'},note='Remove the larger logical volume we just created')
		shutit.send('lvremove /dev/mapper/newvg1-newvol1snap',{'really':'y'},note='Remove the snapshot volume we just created')

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
		shutit.send('lvresize -r -L +0.4G newvg1/virtualvol2',note='resize the logical volume to add 0.4G to it')
		# -r above takes care of this now
		#shutit.send('df -kh /dev/mapper/newvg1-virtualvol2',note='Even though we have resized the logical volume, the filesystem (df) still gives us the same size as previously ~1G.')
		#shutit.send('resize2fs /dev/mapper/newvg1-virtualvol2',note='Resize the filesystem to reflect the new size of the logical volume. You could also add -r/--resize to the lvresize command.')
		shutit.send('df -kh /dev/mapper/newvg1-virtualvol2',note='The size of the logical volume is now reflected in the filesystem')
		shutit.send('dd if=/dev/urandom of=/mnt/thinvol2_dir/afile bs=1M count=1100',note='Now the file creation should work.')
		# snapshotting
		#shutit.send('lvresize -L +10G newvg1/virtualvol2',note='resize the logical volume to add 2G to it')
		#shutit.send('resize2fs /dev/mapper/newvg1-virtualvol2',note='Resize the filesystem to reflect the new size of the logical volume. You could also add -r/--resize to the lvresize command.')
		#shutit.send('lvcreate -s -n vvol2snap -L 2G newvg1/virtualvol2')
		#shutit.pause_point('lvcreate -s -n vvol2snap -L 2G newvg1/virtualvol2')
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

