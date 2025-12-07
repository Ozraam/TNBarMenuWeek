export type MenuColors = {
	background: string;
	primary: string;
	secondary: string;
	text: string;
};

export type MenuGridConfig = {
	rows: number;
	cols: number;
	cell_width: number;
	cell_height: number;
	y_start: number;
};

export type MenuLayoutConfig = {
	image_size: [number, number];
	title_position: [number, number];
	title_text: string;
	title_font_size: number;
	week_text_position: [number, number];
	week_text_anchor: string;
	week_font_size: number;
	grid: MenuGridConfig;
	day_font_size: number;
	content_font_size: number;
	max_text_width: number;
	content_spacing: number;
};

export type MenuStyleConfig = {
	colors: MenuColors;
	layouts: {
		vertical: MenuLayoutConfig;
		horizontal: MenuLayoutConfig;
	};
	assets: {
		logo: string;
	};
};

export type MenuItem = {
	text: string;
	is_meal: boolean;
	img?: string;
};

export type MenuCell = {
	label: string;
	items: MenuItem[];
};

export type MealOption = {
	name: string;
	image: string;
};

export type Ingredient = [string, string, string]; // [name, french description, english description]
