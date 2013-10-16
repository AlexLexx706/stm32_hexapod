#include "animation.h"
#include "stm32f10x_conf.h"
#include <stdlib.h>
#include <string.h>

void InitServosAnimations(struct ServosAnimations * servos_animations)
{
	assert_param(servos_animations);
	servos_animations->count = 0;
	servos_animations->animations = NULL;
	servos_animations->cur_time = 0.0;
	servos_animations->min_time = 0.0;
	servos_animations->max_time = 0.0;

}


int AddAnimation(struct ServosAnimations * servos_animations, uint8_t servo_number, struct AnimationData * data)
{
	assert_param(servos_animations);
	assert_param(data);

	//не верное время
	if (data->time < 0 )
		return 2;

	struct AnimationSet * set = servos_animations->animations;
	struct AnimationSet * end = &servos_animations->animations[servos_animations->count];

	//анимация существует.
	for ( ; set < end; set++ )
	{

		//анимация существует
		if (set->servo_number == servo_number )
		{

			//неправильное время.
			if ( set->count &&
				 data->time <=  set->animation[set->count-1].time )
				return 2;

			struct AnimationData * new_ptr = (struct AnimationData *)realloc(set->animation,
					(set->count + 1) * sizeof(struct AnimationData));

			//ошибка выделения памяти
			if ( new_ptr == NULL )
				return 1;

			set->animation = new_ptr;
			set->animation[set->count] = *data;
			set->count++;
			return 0;
		}
	}

	//новая анимация.
	struct AnimationSet * new_ptr = (struct AnimationSet *)realloc(servos_animations->animations,
			(servos_animations->count + 1) * sizeof(struct AnimationSet));

	if ( new_ptr == NULL )
		return 1;

	servos_animations->animations = new_ptr;
	servos_animations->animations[servos_animations->count].servo_number = servo_number;
	servos_animations->animations[servos_animations->count].animation = malloc(sizeof(struct AnimationData));


	//ошибка выделения памяти
	if ( servos_animations->animations[servos_animations->count].animation == NULL )
	{
		servos_animations->count++;
		servos_animations->animations[servos_animations->count].count = 0;
		return 1;
	}

	servos_animations->animations[servos_animations->count].animation[0] = *data;
	servos_animations->animations[servos_animations->count].count = 1;
	servos_animations->count++;
	return 0;
}

int ClearAnimation(struct ServosAnimations * servos_animations, uint8_t servo_number)
{
	assert_param(servos_animations);

	//анимация существует.
	struct AnimationSet * set = servos_animations->animations;
	struct AnimationSet * end = &servos_animations->animations[servos_animations->count];
	struct AnimationSet * next;


	for ( ; set < end; set++ )
	{
		//анимация существует
		if (set->servo_number == servo_number )
		{
			free(set->animation);

			next = set + 1;

			//переносим данные.
			for ( ; next < end; next++)
			{
				memcpy(set, next, sizeof(struct AnimationSet));
			}

			//перераспределим память
			servos_animations->count--;
			servos_animations->animations = realloc(servos_animations->animations, sizeof(struct AnimationSet) * servos_animations->count);

			if ( servos_animations->count == 0 )
				servos_animations->animations = NULL;

			return 0;
		}
	}
	return 1;
}

void ClearAllAnimation(struct ServosAnimations * servos_animations)
{
	assert_param(servos_animations);

	if (servos_animations->count == 0)
		return;

	struct AnimationSet * set = servos_animations->animations;
	struct AnimationSet * end = &servos_animations->animations[servos_animations->count];

	//анимация существует.
	for ( ; set < end; set++ )
	{
		free(set->animation);
	}

	free(servos_animations->animations);
	servos_animations->count = 0;
	servos_animations->animations = NULL;
}

float GetValue(const struct ServosAnimations * servos_animations, uint8_t servo_number)
{
	assert_param(servos_animations);

	if (servos_animations->count == 0)
		return 0.0;

	struct AnimationSet * a_set = servos_animations->animations;
	struct AnimationSet * end = &servos_animations->animations[servos_animations->count];
	struct AnimationData * p1;
	struct AnimationData * p2;
	struct AnimationData * p_end;

	for ( ; a_set < end; a_set++ )
	{
		if ( a_set->servo_number == servo_number )
		{
			//пусто
			if ( a_set->count == 0 )
				return 0;

			//одно значение.
			if ( a_set->count == 1 || servos_animations->cur_time < a_set->animation->time )
				return a_set->animation->value;

			//просмотр пар
			p1 = a_set->animation;
			p2 = p1 + 1;
			p_end = &a_set->animation[a_set->count];

			for (; p2 < p_end; p2++)
			{
				//время в границах
				if ( servos_animations->cur_time >= p1->time &&
						servos_animations->cur_time < p2->time )
				{
					return p1->value + (p2->value - p1->value) *
							(servos_animations->cur_time - p1->time) / (p2->time - p1->time);
				}
				p1 = p2;
			}
			return p1->value;
		}
	}
	return 0.0;
}
