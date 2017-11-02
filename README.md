# auto_encoder_switch

Script for a situation where a motion encoder needs to remain off unless the motor is moving using EPICS and pyca.  Turns encoder on, moves motor in specified direction and turns encoder back off once IOC reports motor is done moving.
