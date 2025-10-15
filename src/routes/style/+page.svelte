<script lang="ts">
    import { onMount } from "svelte";
    import { buildApiUrl } from "$lib/api";

    type LayoutGrid = {
        rows: number;
        cols: number;
        cell_width: number;
        cell_height: number;
        y_start: number;
    };

    type LayoutConfig = {
        image_size: [number, number];
        title_position: [number, number];
        title_text: string;
        title_font_size: number;
        week_text_position: [number, number];
        week_text_anchor: string;
        week_font_size: number;
        grid: LayoutGrid;
        day_font_size: number;
        content_font_size: number;
        max_text_width: number;
        content_spacing: number;
    };

    type StyleAssets = {
        logo: string;
    };

    type StyleConfig = {
        colors: Record<string, string>;
        layouts: Record<string, LayoutConfig>;
        assets: StyleAssets;
    };

    type PairField = "image_size" | "title_position" | "week_text_position";
    type NumericField =
        | "title_font_size"
        | "week_font_size"
        | "day_font_size"
        | "content_font_size"
        | "max_text_width"
        | "content_spacing";
    type GridField = "rows" | "cols" | "cell_width" | "cell_height" | "y_start";
    type StringField = "title_text" | "week_text_anchor";

    let styleConfig = $state<StyleConfig | null>(null);
    let isLoading = $state(true);
    let isSaving = $state(false);
    let loadError = $state("");
    let statusMessage = $state("");
    let statusError = $state("");
    let validationErrors = $state<string[]>([]);
    let isUploadingLogo = $state(false);
    let logoUploadMessage = $state("");
    let logoUploadError = $state("");

    onMount(() => {
        fetchConfig();
    });

    async function readJson(response: Response) {
        const contentType = response.headers.get("content-type") ?? "";
        if (!contentType.toLowerCase().includes("application/json")) {
            return null;
        }

        try {
            return await response.clone().json();
        } catch (error) {
            console.warn("Impossible d'interpreter la reponse JSON", error);
            return null;
        }
    }

    async function fetchConfig() {
        isLoading = true;
        loadError = "";
        statusMessage = "";
        statusError = "";
        validationErrors = [];
    logoUploadMessage = "";
    logoUploadError = "";

        try {
            const response = await fetch(buildApiUrl("/styleConfig"));
            if (!response.ok) {
                const data = await readJson(response);
                loadError =
                    (data && typeof data === "object" && "message" in data && String(data.message)) ||
                    "Impossible de charger la configuration du style.";
                return;
            }

            const data = (await readJson(response)) as StyleConfig | null;
            if (data) {
                styleConfig = data;
            }
        } catch (error) {
            console.error("Failed to fetch style config", error);
            loadError = "Impossible de charger la configuration du style.";
        } finally {
            isLoading = false;
        }
    }

    function updateColor(key: string, value: string) {
        if (!styleConfig) {
            return;
        }

        styleConfig = {
            ...styleConfig,
            colors: {
                ...styleConfig.colors,
                [key]: value.trim() || styleConfig.colors[key]
            }
        };
    }

    function mutateLayout(layoutKey: string, mutator: (layout: LayoutConfig) => LayoutConfig) {
        if (!styleConfig) {
            return;
        }

        const currentLayout = styleConfig.layouts[layoutKey];
        if (!currentLayout) {
            return;
        }

        styleConfig = {
            ...styleConfig,
            layouts: {
                ...styleConfig.layouts,
                [layoutKey]: mutator(currentLayout)
            }
        };
    }

    function getInputValue(event: Event): string {
        const target = event.currentTarget as HTMLInputElement | HTMLTextAreaElement;
        return target.value;
    }

    function getNumberValue(event: Event): number {
        const target = event.currentTarget as HTMLInputElement;
        return target.valueAsNumber;
    }

    function updatePair(layoutKey: string, field: PairField, index: number, value: number) {
        if (!Number.isFinite(value)) {
            return;
        }

        mutateLayout(layoutKey, (layout) => {
            const next = { ...layout };
            const pair = [...layout[field]] as [number, number];
            pair[index] = Math.round(value);
            return { ...next, [field]: pair };
        });
    }

    function updateNumeric(layoutKey: string, field: NumericField, value: number) {
        if (!Number.isFinite(value)) {
            return;
        }

        mutateLayout(layoutKey, (layout) => ({
            ...layout,
            [field]: Math.round(value)
        }));
    }

    function updateGrid(layoutKey: string, field: GridField, value: number) {
        if (!Number.isFinite(value)) {
            return;
        }

        mutateLayout(layoutKey, (layout) => ({
            ...layout,
            grid: {
                ...layout.grid,
                [field]: Math.round(value)
            }
        }));
    }

    function updateString(layoutKey: string, field: StringField, value: string) {
        mutateLayout(layoutKey, (layout) => ({
            ...layout,
            [field]: value
        }));
    }

    function updateLogoPath(value: string) {
        if (!styleConfig) {
            return;
        }

        styleConfig = {
            ...styleConfig,
            assets: {
                ...styleConfig.assets,
                logo: value.trim()
            }
        };
    }

    async function handleLogoFileSelect(event: Event) {
        const target = event.currentTarget as HTMLInputElement;
        const file = target.files?.[0] ?? null;
        target.value = "";

        if (!file) {
            return;
        }

        isUploadingLogo = true;
        logoUploadMessage = "";
        logoUploadError = "";

        const formData = new FormData();
        formData.append("imageFile", file, file.name);
        const baseName = file.name.replace(/\.[^.]+$/, "");
        formData.append("name", baseName);

        try {
            const response = await fetch(buildApiUrl("/logo"), {
                method: "POST",
                body: formData
            });

            const data = await readJson(response);
            if (!response.ok) {
                logoUploadError =
                    (data && typeof data === "object" && "message" in data && String(data.message)) ||
                    "Impossible de mettre à jour le logo.";
                return;
            }

            const message = (data && typeof data === "object" && "message" in data && String(data.message)) ||
                "Logo mis à jour.";

            if (data && typeof data === "object" && "config" in data && data.config) {
                styleConfig = data.config as StyleConfig;
            } else if (styleConfig && data && typeof data === "object" && data.logo) {
                const logoPath = String((data.logo as Record<string, unknown>).path ?? styleConfig.assets.logo);
                updateLogoPath(logoPath);
            }

            logoUploadMessage = message;
        } catch (error) {
            console.error("Failed to upload logo", error);
            logoUploadError = "Impossible de mettre à jour le logo.";
        } finally {
            isUploadingLogo = false;
        }
    }

    async function handleSubmit(event: Event) {
        event.preventDefault();
        if (!styleConfig) {
            return;
        }

        isSaving = true;
        statusMessage = "";
        statusError = "";
        validationErrors = [];

        try {
            const response = await fetch(buildApiUrl("/styleConfig"), {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(styleConfig)
            });

            const data = await readJson(response);
            if (!response.ok) {
                statusError =
                    (data && typeof data === "object" && "message" in data && String(data.message)) ||
                    "Impossible d'enregistrer la configuration du style.";

                if (data && typeof data === "object" && "errors" in data && Array.isArray(data.errors)) {
                    validationErrors = data.errors.map((err) => String(err));
                }
                return;
            }

            if (data && typeof data === "object") {
                if ("config" in data && data.config) {
                    styleConfig = data.config as StyleConfig;
                }
                statusMessage = "message" in data ? String(data.message) : "Configuration enregistree.";
            } else {
                statusMessage = "Configuration enregistree.";
            }
        } catch (error) {
            console.error("Failed to save style config", error);
            statusError = "Impossible d'enregistrer la configuration du style.";
        } finally {
            isSaving = false;
        }
    }
</script>

<main class="rounded-lg border flex-1 p-6 border-gray-100 bg-gray-600/20 bg-clip-padding backdrop-blur-md backdrop-filter overflow-auto">
    <div class="flex items-center justify-between gap-4 flex-wrap">
        <h2 class="text-3xl font-bold">Configuration du style</h2>
        <button
            type="button"
            class="rounded-md border border-transparent bg-slate-800 px-4 py-2 text-sm text-white shadow-sm transition-all hover:bg-slate-700 hover:shadow-lg focus:bg-slate-700 focus:shadow-none active:bg-slate-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
            onclick={() => fetchConfig()}
            disabled={isLoading || isSaving}
        >
            Recharger la configuration
        </button>
    </div>

    {#if loadError}
        <p class="mt-4 rounded border border-red-400/30 bg-red-500/20 px-4 py-3 text-sm text-red-100">{loadError}</p>
    {/if}

    {#if isLoading && !styleConfig}
        <p class="mt-6 text-sm text-gray-200">Chargement de la configuration...</p>
    {:else if styleConfig}
        <form class="mt-6 space-y-8" onsubmit={handleSubmit}>
            <section class="space-y-4">
                <header>
                    <h3 class="text-xl font-semibold">Couleurs</h3>
                    <p class="text-sm text-gray-200">Definissez les couleurs utilisees pour le fond, les titres et les textes.</p>
                </header>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {#each Object.entries(styleConfig.colors) as [colorKey, value]}
                        <label class="flex flex-col gap-2 text-sm">
                            <span class="font-medium uppercase tracking-wide">{colorKey}</span>
                            <div class="flex items-center gap-3">
                                <input
                                    type="color"
                                    value={value}
                                    oninput={(event) => updateColor(colorKey, getInputValue(event))}
                                    class="h-10 w-16 cursor-pointer rounded border border-white/20 bg-transparent"
                                />
                                <input
                                    type="text"
                                    value={value}
                                    oninput={(event) => updateColor(colorKey, getInputValue(event))}
                                    class="flex-1 rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </div>
                        </label>
                    {/each}
                </div>
            </section>

            <section class="space-y-4">
                <header>
                    <h3 class="text-xl font-semibold">Logo principal</h3>
                    <p class="text-sm text-gray-200">
                        Choisissez le logo affiché sur les menus. Le chemin est relatif au dossier du générateur.
                    </p>
                </header>

                <div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] items-end">
                    <label class="flex flex-col gap-2 text-sm">
                        <span class="font-medium uppercase tracking-wide">Chemin relatif</span>
                        <input
                            type="text"
                            value={styleConfig.assets.logo}
                            oninput={(event) => updateLogoPath(getInputValue(event))}
                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                    </label>

                    <label class="flex flex-col gap-2 text-sm">
                        <span class="font-medium uppercase tracking-wide">Importer un logo</span>
                        <input
                            type="file"
                            accept="image/*"
                            onchange={handleLogoFileSelect}
                            disabled={isUploadingLogo}
                            class="block w-full text-sm text-gray-300 file:mr-4 file:rounded-md file:border-0 file:bg-orange-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-orange-500"
                        />
                    </label>
                </div>

                {#if logoUploadMessage}
                    <p class="text-sm text-green-200">{logoUploadMessage}</p>
                {/if}
                {#if logoUploadError}
                    <p class="text-sm text-red-200">{logoUploadError}</p>
                {/if}
            </section>

            <section class="space-y-5">
                <header>
                    <h3 class="text-xl font-semibold">Mises en page</h3>
                    <p class="text-sm text-gray-200">Ajustez les parametres pour les formats vertical et horizontal.</p>
                </header>

                {#each Object.entries(styleConfig.layouts) as [layoutKey, layout]}
                    <div class="rounded-lg border border-white/15 bg-white/5 p-5 space-y-6">
                        <h4 class="text-lg font-semibold capitalize">{layoutKey}</h4>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                            <div class="space-y-4">
                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Largeur</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.image_size[0]}
                                            oninput={(event) => updatePair(layoutKey, "image_size", 0, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Hauteur</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.image_size[1]}
                                            oninput={(event) => updatePair(layoutKey, "image_size", 1, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Position titre X</span>
                                        <input
                                            type="number"
                                            value={layout.title_position[0]}
                                            oninput={(event) => updatePair(layoutKey, "title_position", 0, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Position titre Y</span>
                                        <input
                                            type="number"
                                            value={layout.title_position[1]}
                                            oninput={(event) => updatePair(layoutKey, "title_position", 1, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>

                                <label class="flex flex-col text-sm gap-2">
                                    <span class="font-medium">Texte du titre</span>
                                    <textarea
                                        rows={3}
                                        value={layout.title_text}
                                        oninput={(event) => updateString(layoutKey, "title_text", getInputValue(event))}
                                        class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                    ></textarea>
                                </label>

                                <label class="flex flex-col text-sm gap-1">
                                    <span class="font-medium">Taille de police du titre</span>
                                    <input
                                        type="number"
                                        min="0"
                                        value={layout.title_font_size}
                                        oninput={(event) => updateNumeric(layoutKey, "title_font_size", getNumberValue(event))}
                                        class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                    />
                                </label>
                            </div>

                            <div class="space-y-4">
                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Position semaine X</span>
                                        <input
                                            type="number"
                                            value={layout.week_text_position[0]}
                                            oninput={(event) => updatePair(layoutKey, "week_text_position", 0, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Position semaine Y</span>
                                        <input
                                            type="number"
                                            value={layout.week_text_position[1]}
                                            oninput={(event) => updatePair(layoutKey, "week_text_position", 1, getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Ancre du texte semaine</span>
                                        <input
                                            type="text"
                                            value={layout.week_text_anchor}
                                            oninput={(event) => updateString(layoutKey, "week_text_anchor", getInputValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Taille police semaine</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.week_font_size}
                                            oninput={(event) => updateNumeric(layoutKey, "week_font_size", getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Taille police jour</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.day_font_size}
                                            oninput={(event) => updateNumeric(layoutKey, "day_font_size", getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Taille police contenu</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.content_font_size}
                                            oninput={(event) => updateNumeric(layoutKey, "content_font_size", getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>

                                <div class="grid grid-cols-2 gap-4">
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Largeur max texte</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.max_text_width}
                                            oninput={(event) => updateNumeric(layoutKey, "max_text_width", getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                    <label class="flex flex-col text-sm gap-1">
                                        <span class="font-medium">Espacement contenu</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={layout.content_spacing}
                                            oninput={(event) => updateNumeric(layoutKey, "content_spacing", getNumberValue(event))}
                                            class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                        />
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                            <label class="flex flex-col text-sm gap-1">
                                <span class="font-medium">Lignes</span>
                                <input
                                    type="number"
                                    min="1"
                                    value={layout.grid.rows}
                                    oninput={(event) => updateGrid(layoutKey, "rows", getNumberValue(event))}
                                    class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </label>
                            <label class="flex flex-col text-sm gap-1">
                                <span class="font-medium">Colonnes</span>
                                <input
                                    type="number"
                                    min="1"
                                    value={layout.grid.cols}
                                    oninput={(event) => updateGrid(layoutKey, "cols", getNumberValue(event))}
                                    class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </label>
                            <label class="flex flex-col text-sm gap-1">
                                <span class="font-medium">Largeur cellule</span>
                                <input
                                    type="number"
                                    min="0"
                                    value={layout.grid.cell_width}
                                    oninput={(event) => updateGrid(layoutKey, "cell_width", getNumberValue(event))}
                                    class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </label>
                            <label class="flex flex-col text-sm gap-1">
                                <span class="font-medium">Hauteur cellule</span>
                                <input
                                    type="number"
                                    min="0"
                                    value={layout.grid.cell_height}
                                    oninput={(event) => updateGrid(layoutKey, "cell_height", getNumberValue(event))}
                                    class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </label>
                            <label class="flex flex-col text-sm gap-1">
                                <span class="font-medium">Depart Y</span>
                                <input
                                    type="number"
                                    min="0"
                                    value={layout.grid.y_start}
                                    oninput={(event) => updateGrid(layoutKey, "y_start", getNumberValue(event))}
                                    class="rounded border border-white/20 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </label>
                        </div>
                    </div>
                {/each}
            </section>

            {#if statusError}
                <div class="rounded border border-red-400/30 bg-red-500/20 px-4 py-3 text-sm text-red-100">
                    <p>{statusError}</p>
                    {#if validationErrors.length}
                        <ul class="mt-2 list-disc pl-5 space-y-1">
                            {#each validationErrors as item}
                                <li>{item}</li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            {/if}

            {#if statusMessage}
                <p class="rounded border border-emerald-400/30 bg-emerald-500/20 px-4 py-3 text-sm text-emerald-100">{statusMessage}</p>
            {/if}

            <div class="flex items-center gap-4">
                <button
                    type="submit"
                    class="rounded-md border border-transparent bg-orange-600 px-5 py-2 text-sm text-white shadow-sm transition-all hover:bg-orange-500 hover:shadow-lg focus:bg-orange-500 focus:shadow-none active:bg-orange-500 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
                    disabled={isSaving}
                >
                    {#if isSaving}
                        <svg class="mr-2 inline h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Sauvegarde...
                    {:else}
                        Sauvegarder les changements
                    {/if}
                </button>
            </div>
        </form>
    {/if}
</main>
