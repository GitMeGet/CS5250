#include <linux/module.h> 
#include <linux/kernel.h> 
#include <linux/init.h> 
#include <linux/slab.h> 
#include <linux/errno.h> 
#include <linux/types.h> 
#include <linux/fs.h> 
#include <linux/proc_fs.h> 
#include <asm/uaccess.h> 
#include <linux/uaccess.h>
  
#define MAJOR_NUMBER 61 
  
/* forward declaration */ 
int onebyte_open(struct inode *inode, struct file *filep); 
int onebyte_release(struct inode *inode, struct file *filep); 
ssize_t onebyte_read(struct file *filep, char *buf, size_t count, loff_t *f_pos); 
ssize_t onebyte_write(struct file *filep, const char *buf, size_t count, loff_t *f_pos); 
static void onebyte_exit(void); 
  
/* definition of file_operation structure */ 
struct file_operations onebyte_fops = { 
	read: onebyte_read, 
	write: onebyte_write, 
	open: onebyte_open, 
	release: onebyte_release 
}; 
  
char *onebyte_data = NULL; 
  
int onebyte_open(struct inode *inode, struct file *filep) 
{ 
	return 0; // always successful 
} 
  
int onebyte_release(struct inode *inode, struct file *filep) 
{ 
	return 0; // always successful 
} 
  
ssize_t onebyte_read(struct file *filep, char *buf, size_t count, loff_t *f_pos) 
{ 	
	int error_count = 0;
	
	// check if buf has been written to by previous call to onebyte_read()
	// but what if i want to write 0 (null char) ?
	if (*buf != 0)
		return 0;

	if (onebyte_data == NULL){
		printk(KERN_INFO "onebyte: onebyte_data is a null ptr\n");
		return -EFAULT;
	}

	// copy_to_user has the format ( * to, *from, size) and returns 0 on success
	error_count = copy_to_user(buf, onebyte_data, sizeof(char));

	if (error_count==0){
		return sizeof(char);
	}
	else {
	  printk(KERN_INFO "onebyte: failed to send %d char to user\n", error_count);
	  return -EFAULT;
	}
} 
ssize_t onebyte_write(struct file *filep, const char *buf, size_t count, loff_t *f_pos) 
{ 
	// get first char from user buffer
	copy_from_user(onebyte_data, buf, sizeof(char));

	if (count > sizeof(char)) {
		printk(KERN_INFO "No space left on device\n");
		return -ENOSPC;
	}
	return sizeof(char);
} 
  
static int onebyte_init(void) 
{ 
	int result; 
	// register the device 
	result = register_chrdev(MAJOR_NUMBER, "onebyte", &onebyte_fops); 

	if (result < 0) { 
		return result; 
	} 

	// allocate one byte of memory for storage 
	// kmalloc is just like malloc, the second parameter is 
	// the type of memory to be allocated. 
	// To release the memory allocated by kmalloc, use kfree. 
	onebyte_data = kmalloc(sizeof(char), GFP_KERNEL); 

	if (!onebyte_data) { 
		onebyte_exit(); 
		// cannot allocate memory 
		// return no memory error, negative signify a failure 
		return -ENOMEM; 
	} 

	// initialize the value to be X 
	*onebyte_data = 'X'; 
	printk(KERN_ALERT "This is a onebyte device module\n"); 
	return 0; 
} 
  
static void onebyte_exit(void) 
{ 
	 // if the pointer is pointing to something 
	 if (onebyte_data) { 
		 // free the memory and assign the pointer to NULL 
		 kfree(onebyte_data); 
		 onebyte_data = NULL; 
	} 
	 // unregister the device 
	 unregister_chrdev(MAJOR_NUMBER, "onebyte"); 
	 printk(KERN_ALERT "Onebyte device module is unloaded\n"); 
} 
  
MODULE_LICENSE("GPL"); 

module_init(onebyte_init); 
module_exit(onebyte_exit);