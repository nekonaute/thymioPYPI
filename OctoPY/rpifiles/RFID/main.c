#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>
#include <fcntl.h>
#include <stdio.h>
#include <signal.h>
#include <time.h>
#include <string.h>
#include <getopt.h>
#include <termios.h>
#include <errno.h>
#include "serial_read.h"

static volatile int g_running=1;

void sig_handler(int signum)
{
	//if(signum == SIGINT)
	//{
		g_running = 0;
	//}
}

int main(int argc, char* argv[])
{

char stockage_instructions[512];
FILE *fp, *fp_test, *fp_pid;

//int g_pid;
int incr_char=0, i_tab=0;

char  serialportname[256], instructionsfile[256];

char cmd[256];

strcpy(serialportname, argv[1]);
strcpy(instructionsfile, argv[2]);

signal(SIGINT, sig_handler);
/******* COMM SERIE *******************/

	const int buf_max = 256;
	int fd = -1;
	char serialport[buf_max];
	int baudrate = 9600; //defaut
	char quiet = 0;
	char eolchar = '\n';
	int timeout = 10000;
	char buf[buf_max];
	//int rc,n;

/*************************************/


	if((fp_test = fopen("/home/dianoux/Documents/Programmation/comm_serial_RFID/RFID.txt","w")) ==NULL){perror("Impossible d ouvrir fichier de log");}


	/****INITIALISATION DU PORT SÉRIE******/
	if(fd!=-1){
		serialport_close(fd);
		if(!quiet) printf("port clos %s\n", serialport);
	}
	strcpy(serialport, "/dev/ttyUSB0");
	//strcpy(serialport, serialportname);
	//fd = serialport_init("/dev/ttyUSB0", baudrate);
	fd = serialport_init(serialportname, baudrate);
	if(fd == -1) printf("impossible d ouvrir le port%s\n", serialport);
	fprintf(fp_test,"port ouvert %s\n", serialportname);
	printf("port ouvert: %s\n", serialportname);
	serialport_flush(fd);
	memset(buf, 10, buf_max);
	char b[6];

	

		while(g_running)
		{
			int n = read(fd, b, 6);
			if( n==-1) {
				if(errno == EINTR)
				{
				fprintf(fp_test,"signal reçu, g_running == %d", g_running); 
				}
				printf("signal SINGTERM");
			}
			if( n==0 ) {
			      usleep( 1 * 100 ); // wait 1 msec try again
				//timeout--;
				continue;
			}
			if(n!=0){
				printf("car: %i\n", b[0]);
				stockage_instructions[incr_char]=b[0];
				incr_char = incr_char+1;
				//fprintf(fp_test, "increment de caractere: %d\n", incr_char);
			}

		}
		printf("Interruption...\n");
		serialport_close(fd);
				if((fp = fopen(instructionsfile,"w")) ==NULL)
				{
					printf("Impossible d'ouvrir le fichier de sortie\n");
					exit(1);
				}
				fprintf(fp, "Ecriture OK\n");
				for(i_tab = 0; i_tab<incr_char; i_tab++){fprintf(fp, "%i\n", stockage_instructions[i_tab]);}
				fprintf(fp, "FIN\n");
				fclose(fp);
				//fprintf(fp_test, "signal de fin de fichier\n");
		fprintf(fp_test, "port clos");
		printf("port clos");
		fclose(fp_test);
return 1;
}
