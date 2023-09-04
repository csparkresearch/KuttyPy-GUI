/*
* TWI_Test.c
*
* Created: 08-Jun-19 10:06:47 AM
* Author : TEP SOVICHEA
*/
#define F_CPU	8000000		// 8 MHz clock 

#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>

#include "mh-uart.c"
#include "mh-i2c.c"

#define MPU6050_ADDR	0x68

// MPU6050 register address
#define ACCEL_XOUT_H	0x3B
#define ACCEL_XOUT_L	0x3C
#define ACCEL_YOUT_H	0x3D
#define ACCEL_YOUT_L	0x3E
#define ACCEL_ZOUT_H	0x3F
#define ACCEL_ZOUT_L	0x40
#define PWR_MGMT_1		0x6B

typedef struct
{
	uint16_t x;
	uint16_t y;
	uint16_t z;
} mpu_data_t;

void mpu_init(void);
void mpu_get_accel_raw(mpu_data_t* mpu_data);
void mpu_get_accel(mpu_data_t* mpu_data);


/************************************************************************/
/*							Function definitions                        */
/************************************************************************/


void mpu_init(void)
{
	uint8_t data[2] = {PWR_MGMT_1, 0};
	tw_master_transmit(MPU6050_ADDR, data, sizeof(data), false);
}


void mpu_get_accel_raw(mpu_data_t* mpu_data)
{
	/* 2 registers for each of accel x, y and z data */
	uint8_t data[6];
	
	data[0] = ACCEL_XOUT_H;
	tw_master_transmit(MPU6050_ADDR, data, 1, true);
	_delay_ms(1);
	
	tw_master_receive(MPU6050_ADDR, data, sizeof(data));
	
	/* Default accel config +/- 2g */
	mpu_data->x = (int16_t)(((uint16_t)data[0]&0xFF) << 8 | data[1]&0xFF) ;
	mpu_data->y = (int16_t)(((uint16_t)data[2]&0xFF) << 8 | data[3]&0xFF) ;
	mpu_data->z = (int16_t)(((uint16_t)data[4]&0xFF) << 8 | data[5]&0xFF) ;

}


void mpu_get_accel(mpu_data_t* mpu_data)
{
	mpu_get_accel_raw(mpu_data);
	//mpu_data->x = mpu_data->x; //raw data
}


/************************************************************************/
/*							Main application                            */
/************************************************************************/

int main(void)
{
	char out_str[50] = {0};
	/* Initialize UART */
	
	/* Initialize project configuration */
	tw_init(TW_FREQ_400K, true); // set I2C Frequency, enable internal pull-up
	uart_init(38400);
	uart_send_string("--------------- Application Started ---------------\n");
	mpu_init();
	mpu_data_t accel;	
	
	uart_send_string("Read accelerometer data.\n");
	while (1)
	{
		mpu_get_accel(&accel);
		//sprintf(out_str, "Accel X: %d, %d, %d\n", accel.x, accel.y, accel.z);
		sprintf(out_str, "%d\n", accel.x);
		uart_send_string(out_str);
		_delay_ms(20);
	}
}