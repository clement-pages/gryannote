<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import type { ButtonEvent, AxeEvent } from "./types";

    export let paused: boolean = true;
    // i-th is true if i-th button is pressed, false otherwise
    let buttonState: boolean[];
    let axeValue: number[];
    let gamepad: Gamepad;

    let dispatch = createEventDispatcher<{
        "buttonPressed": ButtonEvent,
        "buttonReleased": ButtonEvent,
        "axesValueUpdated": AxeEvent,
        "axeReleased": AxeEvent,
        "axePushed": AxeEvent,
    }>();

    function checkButtonEvent(): void {
        for(let idx = 0; idx < gamepad.buttons.length; idx++){
            const button = gamepad.buttons[idx];
            const isPressed = button.pressed;
            // button press event
            if(isPressed && !buttonState[idx]){
                dispatch("buttonPressed", {idx});
            }
            // button release event
            else if(!isPressed && buttonState[idx]) {
                dispatch("buttonReleased", {idx});
            }

            buttonState[idx] = isPressed;
        }
    }

    function checkAxeEvent(): void {
        for(let idx = 0; idx < gamepad.axes.length; idx++){
            const value = gamepad.axes[idx];
            // 0.01 represent the dead zone
            if(Math.abs(value) < 0.01 && Math.abs(axeValue[idx]) > 0.01){
                dispatch("axeReleased", {idx, value})
            }
            else if(Math.abs(value) > 0.01){
                dispatch("axePushed", {idx, value})
            }
            else if(Math.abs(value - axeValue[idx]) > 0.01){
                dispatch("axesValueUpdated", {idx, value})
            }

            axeValue[idx] = value;
        }
    }

    function poll(): void {
        if(!paused){
            checkButtonEvent();
            checkAxeEvent();
        }
        window.requestAnimationFrame(poll);
    }

    export function isButtonPressed(idx: number): boolean {
        return buttonState[idx];
    }

    export function isAxePushed(idx: number): boolean {
        return Math.abs(axeValue[idx]) > 0.01;
    }

    export function start(): void {
        window.addEventListener("gamepadconnected", (e: GamepadEvent) => {
            gamepad = e.gamepad;
            console.log(gamepad);
            buttonState = new Array(gamepad.buttons.length).fill(false);
            axeValue = new Array(gamepad.axes.length).fill(0.);
            paused = false;
            poll();
        });
    }

</script>
