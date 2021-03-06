/*
*   Wildfire - The Open Source KNX/EIB-Protocol Stack.
*
*  (C) 2007-2016 by Christoph Schueler <github.com/Christoph2,
*                                       cpu12.gems@googlemail.com>
*
*   All Rights Reserved
*
*  This program is free software; you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation; either version 2 of the License, or
*  (at your option) any later version.
*
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License along
*  with this program; if not, write to the Free Software Foundation, Inc.,
*  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*
*/
#include "Wildfire_Config.h"
#include "knx_timer.h"
#include "knx_defs.h"

void KnxTlc_OnConnectionTimeoutTimer(void);

KnxTmr_CallbackFunctionType KnxTmr_Callbacks[TMR_NUM_TIMERS] = {
    (KnxTmr_CallbackFunctionType)NULL,
#if KNX_STACK_TYPE == KNX_FULL_STACK
    (KnxTmr_CallbackFunctionType)KnxTlc_OnConnectionTimeoutTimer,
#else
    (KnxTmr_CallbackFunctionType)NULL,
#endif
    (KnxTmr_CallbackFunctionType)NULL,
    (KnxTmr_CallbackFunctionType)NULL,
};

#if KNX_TARGET_TYPE == KNX_TARGET_POSIX
#include "port/port_timer.h"

Port_Timer_ConfigType Port_Timer_Configuration = {
    KnxTmr_SystemTickHandler,
    (uint16_t)10
};

#endif

