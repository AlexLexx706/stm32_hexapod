#include <stm32f10x_conf.h>
#include <stm32f10x.h>
#include <stm32f10x_gpio.h>
#include <stm32f10x_rcc.h>
#include <stm32f10x_usart.h>
#include <string.h>
#include <math.h>
#include <stm32f10x_tim.h>
#include <stdio.h>

#include "anumation/animation.h"
#include "servo_controll/servo_controll.h"
#include "common.h"
#include "stm32f10x_spi.h"


//Буфер для приёма сообщения UART2.
uint8_t uart2_rx_buf[40];

//Номер байта UART2 принимаемого в буфер.
uint8_t uart2_rx_bit = 0;

//содержит информацию о сервоприводах.
static struct GroupsData servos_data;

//содержит данные анимации.
//static struct ServosAnimations animations;

//Функция отправляет байт в UART
void send_to_uart(uint8_t data)
{
    while(!(USART2->SR & USART_SR_TC));
    USART2->DR=data;
}

//отправка буффера в UART2
void send_buffer(uint8_t size, uint8_t * buffer)
{
    uint8_t i=0;

    while(i < size)
    {
        send_to_uart(buffer[i]);
        i++;
    }
}

//Инициализируем USART2
void init_usart(void)
{
    GPIO_InitTypeDef GPIO_InitStructure; //Структура содержащая настройки порта
    USART_InitTypeDef USART_InitStructure; //Структура содержащая настройки USART

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);

    //Конфигурируем PA2 как альтернативную функцию -> TX UART. Подробнее об конфигурации можно почитать во втором уроке.
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);


    //Конфигурируем PA3 как альтернативную функцию -> RX UART. Подробнее об конфигурации можно почитать во втором уроке.
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    //Инициализируем UART с дефолтными настройками: скорость 9600, 8 бит данных, 1 стоп бит
    USART_StructInit(&USART_InitStructure); 

    USART_InitStructure.USART_BaudRate            = 57600;
    USART_InitStructure.USART_WordLength          = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits            = USART_StopBits_1;
    USART_InitStructure.USART_Parity              = USART_Parity_No ;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode                = USART_Mode_Rx | USART_Mode_Tx;

    USART_Init(USART2, &USART_InitStructure);

    //Прерывание по приему
    USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);
    
    //Включаем UART
    USART_Cmd(USART2, ENABLE);

    //Включаем прерывания от UART
    NVIC_EnableIRQ(USART2_IRQn); 
    
    //Прерывание от UART, приоритет 0, самый высокий
    NVIC_SetPriority(USART2_IRQn, 0);
}

void delay(uint32_t i)
{
    volatile uint32_t j;
    for (j=0; j!= i * 1000; j++);
}


void init_SPI1()
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB | RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO | RCC_APB2Periph_SPI1, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    SPI_InitTypeDef SPI_InitStructure;
    SPI_StructInit(&SPI_InitStructure);

    //NSS вход выбор чипа
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_15;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA , &GPIO_InitStructure);

    //CLK
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &GPIO_InitStructure);

    //MISO
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &GPIO_InitStructure);

    //MOSI
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &GPIO_InitStructure);

    GPIO_PinRemapConfig(GPIO_Remap_SPI1, ENABLE);

    //Заполняем структуру с параметрами SPI модуля
    SPI_InitStructure.SPI_Direction = SPI_Direction_2Lines_FullDuplex; //полный дуплекс
    SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b; // передаем по 8 бит
    SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low; // Полярность и
    SPI_InitStructure.SPI_CPHA = SPI_CPHA_1Edge; // фаза тактового сигнала
    SPI_InitStructure.SPI_NSS = SPI_NSS_Hard; // Управлять состоянием сигнала NSS аппаратно
    SPI_InitStructure.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_2; // Предделитель SCK
    SPI_InitStructure.SPI_FirstBit = SPI_FirstBit_MSB; // Первым отправляется старший бит
    SPI_InitStructure.SPI_Mode = SPI_Mode_Slave; // Режим - слейв
    SPI_Init(SPI1, &SPI_InitStructure); //Настраиваем SPI1

    SPI_Cmd(SPI1, ENABLE); // Включаем модуль SPI1....

    SPI_I2S_ITConfig(SPI1, SPI_I2S_IT_RXNE, ENABLE); //Включаем прерывание по приему байта
    NVIC_EnableIRQ(SPI1_IRQn); //Разрешаем прерывания от SPI1

}

//Обработчик прерываний от SPI1
void SPI1_IRQHandler (void)
{
    uint8_t data = SPI_I2S_ReceiveData(SPI1);
    data = data;
}


int main(void)
{
    //инициализация анимации.
    //InitServosAnimations(&animations);


    //Инициализируем UART
    init_usart();

    //инициализация SPI1
    init_SPI1();

    init_servo_data(&servos_data);

    //настройка пределов

    struct GroupSettings g0 = {0, 0.02, 240,
            {{0.00039,0.00242,},
            {0.00048, 0.0025},
            {0.00048, 0.00249},
            {0.0004, 0.00242}}};

    set_servo_range(&servos_data, &g0);

    struct GroupSettings g1 = {1, 0.02, 240,
            {{0.00053,0.00255},
            {0.000449,0.00244},
            {0.00048,0.0025},
            {0.000459, 0.00248}}};
    set_servo_range(&servos_data, &g1);

    struct GroupSettings g2 = {2, 0.02, 240,
            {{0.000440, 0.002480},
            {0.000440, 0.002440},
            {0.000510, 0.002460},
            {0.000480,  0.002500}}};
    set_servo_range(&servos_data, &g2);

    struct GroupSettings g3 = {3, 0.02, 240,
            {{0.00048, 0.0025},
            {0.00048, 0.00249},
            {0.000449, 0.00243},
            {0.00047, 0.0025}}};
    set_servo_range(&servos_data, &g3);

    //Глобальное включение прерывания
    SysTick_Config(SystemCoreClock/50);
    __enable_irq();


    //тест порта
    /**
    GPIO_InitTypeDef gpio;
    GPIO_StructInit(&gpio);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
    gpio.GPIO_Pin = GPIO_Pin_10 | GPIO_Pin_11;
    gpio.GPIO_Speed = GPIO_Speed_50MHz;
    gpio.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_Init(GPIOB, &gpio);

    GPIO_SetBits(GPIOB, GPIO_Pin_10 | GPIO_Pin_11);
    */

    GPIO_InitTypeDef PORT;
    //Включаем порты А и С
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC , ENABLE);
    //Настраиваем ноги PC8 и PC9 на выход. Там у нас висят светодиоды
    PORT.GPIO_Pin = GPIO_Pin_0;
    PORT.GPIO_Mode = GPIO_Mode_AIN;
    PORT.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_Init(GPIOC , &PORT);

    RCC_APB2PeriphClockCmd(RCC_APB2ENR_ADC1EN, ENABLE); //Включаем тактирование АЦП
    ADC1->CR2 |= ADC_CR2_CAL; //Запуск калибровки АЦП
    while (!(ADC1->CR2 & ADC_CR2_CAL));
    //Ожидаем окончания калибровки
    ADC1->SMPR2 |= (ADC_SMPR2_SMP1_2 | ADC_SMPR2_SMP1_1 | ADC_SMPR2_SMP1_0); //Задаем
    // длительность выборки
    ADC1->CR2 |= ADC_CR2_JEXTSEL; //Преобразование инжектированной группы
    //запустится установкой бита JSWSTART
    ADC1->CR2 |= ADC_CR2_JEXTTRIG; //Разрешаем внешний запуск инжектированной группы
    ADC1->CR2 |= ADC_CR2_CONT; //Преобразования запускаются одно за другим
    ADC1->CR1 |= ADC_CR1_JAUTO; //Разрешить преобразование инжектированной группы
    //после регулярной. Не понятно зачем, но без этого не работает
    ADC1->JSQR |= (10<<15); //Задаем номер канала (выбран ADC1)
    ADC1->CR2 |= ADC_CR2_ADON;//Теперь включаем АЦП
    ADC1->CR2 |= ADC_CR2_JSWSTART; //Запуск преобразований
    while (!(ADC1->SR & ADC_SR_JEOC)); //ждем пока первое преобразование завершится
    //Теперь можно читать результат из JDR1
    uint32_t adc_res; //Использовал переменную для отладки. Можно и без неё

    while(1)
    {
        adc_res=ADC1->JDR1;
        delay(adc_res);
    }

    while(1)
    {}
}


void TIM1_UP_TIM16_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM1, TIM_IT_Update) != RESET)
    {
        TIM_ClearITPendingBit(TIM1, TIM_IT_Update);
        TIM_SetCompare1(TIM1, servos_data.group[0].servos[0].timer_value);
        TIM_SetCompare2(TIM1, servos_data.group[0].servos[1].timer_value);
        TIM_SetCompare3(TIM1, servos_data.group[0].servos[2].timer_value);
        TIM_SetCompare4(TIM1, servos_data.group[0].servos[3].timer_value);

        //отключим прерывание.
        TIM_ITConfig(TIM1, TIM_IT_Update, DISABLE);
    }
}

void TIM2_IRQHandler(void)
{
    //Если счётчик переполнился, можно смело закидывать в регистр сравнения новое значение.
    if (TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET)
    {
        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
        TIM_SetCompare1(TIM2, servos_data.group[1].servos[0].timer_value);
        TIM_SetCompare2(TIM2, servos_data.group[1].servos[1].timer_value);
        TIM_SetCompare3(TIM2, servos_data.group[1].servos[3].timer_value);
        TIM_SetCompare4(TIM2, servos_data.group[1].servos[2].timer_value);
        TIM_ITConfig(TIM2, TIM_IT_Update, DISABLE);
    }
}



void TIM3_IRQHandler(void)
{
    //Если счётчик переполнился, можно смело закидывать в регистр сравнения новое значение.
    if (TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET)
    {
        TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
        TIM_SetCompare1(TIM3, servos_data.group[2].servos[0].timer_value);
        TIM_SetCompare2(TIM3, servos_data.group[2].servos[1].timer_value);
        TIM_SetCompare3(TIM3, servos_data.group[2].servos[2].timer_value);
        TIM_SetCompare4(TIM3, servos_data.group[2].servos[3].timer_value);
        TIM_ITConfig(TIM3, TIM_IT_Update, DISABLE);
    }
}

void TIM4_IRQHandler(void)
{
    //Если счётчик переполнился, можно смело закидывать в регистр сравнения новое значение.
    if (TIM_GetITStatus(TIM4, TIM_IT_Update) != RESET)
    {
        TIM_ClearITPendingBit(TIM4, TIM_IT_Update);
        TIM_SetCompare1(TIM4, servos_data.group[3].servos[0].timer_value);
        TIM_SetCompare2(TIM4, servos_data.group[3].servos[1].timer_value);
        TIM_SetCompare3(TIM4, servos_data.group[3].servos[2].timer_value);
        TIM_SetCompare4(TIM4, servos_data.group[3].servos[3].timer_value);
        TIM_ITConfig(TIM4, TIM_IT_Update, DISABLE);
    }
}



void USART2_IRQHandler (void)
{
    //Приём байта
    if ( USART_GetITStatus(USART2, USART_IT_RXNE) != RESET )
    {
        char uart_data = USART2->DR;
        //чистим флаг прерывания
        USART_ClearITPendingBit(USART2, USART_IT_RXNE);

        uart2_rx_buf[uart2_rx_bit] = uart_data;
                                                                                                  ++;

        //завершение приёма пакета
        if ( (uart2_rx_buf[0] + 2) == uart2_rx_bit )
        {
            uart2_rx_bit = 0;

            switch (uart2_rx_buf[1])
            {
                //эхо
                case CMD_ECHO:
                {
                    break;
                }
                //установка позиции.
                case CMD_SET_SEVO_POS:
                {
                    if ( uart2_rx_buf[0]  == sizeof(struct ServoPosData))
                        uart2_rx_buf[2] = set_servo_angle(&servos_data, (struct ServoPosData *)&uart2_rx_buf[2]);
                    else
                        uart2_rx_buf[2] = WRONG_CMD_PACKET_SIZE;

                    uart2_rx_buf[0] = 1;
                    break;
                }
                case CMD_SET_SEVOS_RANGES:
                {
                    if ( uart2_rx_buf[0] == sizeof(struct GroupSettings))
                        uart2_rx_buf[2] = set_servo_range(&servos_data, (struct GroupSettings *)&uart2_rx_buf[2]);
                    else
                        uart2_rx_buf[2] = WRONG_CMD_PACKET_SIZE;

                    uart2_rx_buf[0] = 1;
                    break;
                }
                case CMD_ADD_ANIMATION:
                {
                    uart2_rx_buf[0] = 1;
                    uart2_rx_buf[2] = NOT_IMPLEMENTED;
                    break;
                }
                case CMD_CLEAR_ANIMATION:
                {
                    uart2_rx_buf[0] = 1;
                    uart2_rx_buf[2] = NOT_IMPLEMENTED;
                    break;
                }
                case CMD_START_ANIMATIONS:
                {
                    uart2_rx_buf[0] = 1;
                    uart2_rx_buf[2] = NOT_IMPLEMENTED;
                    break;
                }
                case CMD_STOP_ANIMATIONS:
                {
                    uart2_rx_buf[0] = 1;
                    uart2_rx_buf[2] = NOT_IMPLEMENTED;
                    break;
                }
                case CMD_GET_SEVOS_RANGES:
                {
                    uart2_rx_buf[0] = 1;

                    if ( uart2_rx_buf[0] == sizeof(uint8_t) )
                    {
                        uart2_rx_buf[2] = get_servo_range(&servos_data,
                                                            *((uint8_t *)&uart2_rx_buf[2]),
                                                            (struct GroupSettings *)&uart2_rx_buf[3]);
                        if ( uart2_rx_buf[2] == 0 )
                            uart2_rx_buf[0] = 1 + sizeof(struct GroupSettings);
                    }
                    else
                        uart2_rx_buf[2] = WRONG_CMD_PACKET_SIZE;
                    break;
                }
            }
            send_buffer(uart2_rx_buf[0] + 2, uart2_rx_buf);
        }
    }
}

void SysTick_Handler(void)
{
    return;

    struct ServoPosData spd;
    spd.group_id = 0;
    spd.number = 0;
    static float angle = 0.0;
    float len =  0.3f;
    float d_len = (1.f - len) / 2.f;

    spd.value = (cos(angle) + 1.0) / 2.0 * len + d_len;
    angle = angle + 0.05;

    for (; spd.group_id < GROUPS_COUNT; spd.group_id++ )
    {
         spd.number = 0;
        for (; spd.number < SERVOS_COUNT_IN_GROUP; spd.number++ )
        {
            set_servo_angle(&servos_data, &spd);
        }
    }
}
