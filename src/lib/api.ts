const resolvedApiBase = (() => {
    const configured = import.meta.env.VITE_PUBLIC_API_URL?.toString().trim();
    const isBrowser = typeof window !== "undefined";

    if (configured) {
        try {
            const url = new URL(configured, isBrowser ? window.location.origin : undefined);
            const configuredHost = url.hostname;
            const isConfiguredLocal = ["localhost", "127.0.0.1", "0.0.0.0"].indexOf(configuredHost) !== -1;

            if (!isConfiguredLocal) {
                return url.origin.replace(/\/$/, "");
            }

            if (isBrowser) {
                const currentHost = window.location.hostname;
                const isCurrentLocal = ["localhost", "127.0.0.1", "0.0.0.0"].indexOf(currentHost) !== -1;
                if (isCurrentLocal) {
                    return url.origin.replace(/\/$/, "");
                }
            }
        } catch (error) {
            console.warn("VITE_PUBLIC_API_URL is not a valid URL, falling back to inferred host", error);
        }
    }

    if (isBrowser) {
        const { protocol, hostname } = window.location;
        const port = 5000;

        if (hostname !== "localhost" && hostname !== "127.0.0.1" && hostname !== "0.0.0.0") {
            console.log(`${protocol}//${hostname}`.replace("menu.", "menuback."));
            
            return `${protocol}//${hostname}`.replace("menu.", "menuback.");
        }

        return `${protocol}//${hostname}:${port}`
    }

    return "http://localhost:5000";
})();

/** Base URL used for all backend calls from the frontend. */
export const API_BASE = resolvedApiBase;

/** Build an absolute URL for the backend, ensuring we have exactly one slash between base and path. */
export const buildApiUrl = (path: string): string => {
    const normalized = path.charAt(0) === "/" ? path : `/${path}`;
    return `${API_BASE}${normalized}`;
};
