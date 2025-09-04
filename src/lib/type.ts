export type weekOptions = {
    label: string;
    space: DayOptions[];
}

export type DayOptions = {
    is_used: boolean,
    is_meal: boolean,
    text: string,
    meal: string | undefined,
}