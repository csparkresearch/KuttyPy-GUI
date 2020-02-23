/*
 * SHT71.h
 *
 * Created: 12/29/2016 11:57:07 PM
 *  Author: Will Choi
 */ 


#ifndef SHT7X_H_
#define SHT7X_H_

void InitializeSensor();
unsigned char ReadTemperature(double* temperature);
unsigned char ReadHumidity(double* humidity, double temperature);
#endif /* SHT7X_H_ */