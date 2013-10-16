#ifndef __ANIMATION_H_
#define __ANIMATION_H_
#include "stm32f10x.h"

//данные анимации.
struct AnimationData
{
    float time;
    float value;

    struct XXX
    {
    	int i;
    } x[11];
};

//данные анимации
struct AnimationSet
{
    struct AnimationData * animation;
    uint8_t count;
    uint8_t servo_number;
};

struct ServosAnimations
{
    struct AnimationSet * animations;
    uint8_t count;
    float cur_time;
    float min_time;
    float max_time;
};

void InitServosAnimations(struct ServosAnimations * servos_animations);

int AddAnimation(struct ServosAnimations * servos_animations, uint8_t servo_number, struct AnimationData * data);

int ClearAnimation(struct ServosAnimations * servos_animations, uint8_t servo_number);

void ClearAllAnimation(struct ServosAnimations * servos_animations);

float GetValue(const struct ServosAnimations * servos_animations, uint8_t servo_number);

#endif /* __ANIMATION_H_ */
