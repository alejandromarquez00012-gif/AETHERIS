/*
 * Seno_leds_adc_1s_timer.c
 * Lee el ADC exactamente cada 1 s usando la ISR del Timer1 (sin ADC auto-trigger).
 */

#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <stdbool.h>

volatile uint16_t O2_atmosferico = 0;  
int Amplitud=0;
int centro=0;
int a = 0;
bool SEN = false;

int Seno[129] = {
  128,131,134,138,140,144,147,150,153,156,159,162,165,168,171,174,177,180,182,185,188,191,194,196,199,201,204,206,209,211,214,216,
  218,220,222,224,226,228,230,232,234,236,237,239,240,242,243,244,246,247,248,249,250,251,251,252,253,253,254,254,254,255,255,255,
  255,255,255,255,254,254,253,253,252,252,251,250,249,248,247,246,245,244,242,241,240,238,236,235,233,231,229,227,225,223,221,219,
  217,215,212,210,208,205,203,200,197,195,192,189,187,184,181,178,175,172,169,167,164,160,157,154,151,148,145,142,139,136,133,130,128
};


int Senofinal[129][2];

void CONFIG_ADC()
{
	ADMUX  = (1 << REFS0);
	ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
}


void CONFIG_TIMER1_1Hz()
{
	TCCR1A = 0;
	TCCR1B = (1 << WGM12) | (1 << CS12) | (1 << CS10); 
	OCR1A  = 15624;
	TIMSK1 = (1 << OCIE1A); 
}

void CONFIG_TIMER2()
{
	TCCR2A = (1 << WGM21);   
	TCCR2B = (1 << CS20)|(1 << CS21);
	OCR2A  = 38; 
	TIMSK2 = (1 << OCIE2A);
}
ISR(TIMER1_COMPA_vect)
{
	ADCSRA |= (1 << ADSC);
	while (ADCSRA & (1 << ADSC)) 
	{}		
	uint8_t low  = ADCL;
	uint8_t high = ADCH;
	O2_atmosferico = ((uint16_t)high << 8) | low;
	
	Amplitud=0.0293*O2_atmosferico+20;
	
	if (Amplitud<20)
	{
		Amplitud=20;
	}
	else if (Amplitud>50)
	{
		Amplitud=50;
	}
	for (int i = 0; i < 129; i++)
	{
		Senofinal[i][0] = ((Seno[i] - 128) * Amplitud / 50) +128;
		Senofinal[i][1] = 128- ((Seno[i] - 128) * Amplitud / 50);
	}
}

ISR(TIMER2_COMPA_vect)
{
	if (!SEN) 
	{
		PORTD = Senofinal[a][0];
		if (a == 126) 
		{
			SEN = true;
			a=-1;
		}
	} 
	else 
	{
		PORTD = Senofinal[a][1];
		if (a == 126) 
		{
			SEN = false;
			a=-1;
		}
	}
	a++;
}

int main(void)
{
	DDRD = 0xFF;  
	DDRC=0x00;

	CONFIG_ADC();
	CONFIG_TIMER1_1Hz();     
	CONFIG_TIMER2();  
	sei(); 

	while (1) 
	{
    }
  }

