# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 21:24:44 2024

@author: Mert
"""

import cv2
import serial
from pyzbar import pyzbar

def send_binary_to_com(binary_string, com_port):
    try:
        print('\n')
        ser = serial.Serial(com_port, baudrate=9600, timeout=1)
        binary_bytes = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')
        ser.write(binary_bytes)
        print("Scan Results sent successfully.")
        ser.close()
        
    except Exception as e:
        print("An error occurred:", e)
        
        
def receive_data(com_port):
    ser = serial.Serial(com_port, 9600) 
    try:
        while True:
            data = ser.read(5) 
            if data:
                return data.decode('ascii')
    except KeyboardInterrupt:
        ser.close() 


def capture_image():

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    return frame


def find_and_read_barcode(image):

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(grayscale)

    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        return str(barcode_data)
    
    
            
file=open('ticket_database.txt','w')
file.write('TICKET DATABASE \n')
file.close()   
            

if __name__ == "__main__":
    
    com_port = 'COM4'  
    work=True
    
    while work==True:
        data=receive_data(com_port)
        print(data)
    
        if (data == 'snap_'):
            image = capture_image()
            barcode = find_and_read_barcode(image)

            
            room = barcode[0]
            row = barcode[1:3]
            seat = barcode[3:5]
            
            repetition=bool(False)
            
            with open('ticket_database.txt', 'r') as database:
                for line in database:
                    if barcode in line:
                        repetition = True
                        break
            if repetition == False:
                img_name = f'room_{room}_row_{row}_seat_{seat}.jpg'
                database=open('ticket_database.txt','a')
                database.write('Barcode: ' + barcode + '\t' + 'Room: ' + room + '\t' + 'Row: ' + row + '\t' + 'Seat: ' + seat+'\n')
                print('Barcode: ' + barcode + '\n' + 'Room: ' + room + '\n' + 'Row: ' + row + '\n' + 'Seat: ' + seat)
                database.close()
                try:
                    cv2.imwrite(img_name, image)
                    print('\n',"Image saved as:", img_name,'\n')
                except Exception :
                    print("Error saving image")
                    
                send_binary_to_com("01000101", com_port)    #e for enable
                
                
            else:
                img_name = f'DUPLICATE_room_{room}_row_{row}_seat_{seat}.jpg'
                
                print('Barcode: ' + barcode + ' has already been scanned. Access denied.')

                try:
                    cv2.imwrite(img_name, image)
                    print('\n',"Image saved as:", img_name,'\n')
                except Exception :
                    print("Error saving image")
                    
                send_binary_to_com("01010010", com_port)    #r for refuse
        elif (data == 'wait_'):
            work = False
            break
                
            database.close


