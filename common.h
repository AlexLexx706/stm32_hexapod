#ifndef __COMMON_H_
#define __COMMON_H_

//комманды
enum {
    CMD_ECHO = 0,
    CMD_SET_SEVO_POS,
    CMD_SET_SEVOS_RANGES,
    CMD_ADD_ANIMATION,
    CMD_CLEAR_ANIMATION,
    CMD_START_ANIMATIONS,
    CMD_STOP_ANIMATIONS,
    CMD_GET_SEVOS_RANGES,
    CMD_GET_SEVO_POS,
};

//коды ошибок
enum {
    NO_ERROR = 0,
    NOT_IMPLEMENTED,
    WRONG_CMD_PACKET_SIZE,
    WRONG_PARAMS,
    WRONG_SERVO_NUMBER,
    WRONG_SERVO_ANGLE,
    WRONG_GROUP_NUMBER
};

#endif /* __COMMON_H_ */
