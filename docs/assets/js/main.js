// Menu of the blocks of code, opened by an icon at the start of their code-meta, replacing the version of the language:
// - the PHP version whose syntax the code is shown in (<pre class="code" data-php>, see bin/dev/highlight.py):
//   the newest one offered by the package by default ("max"), the minimum one ("min"), each one staying the newest or
//   the minimum one of each page, or another one, the minimum one being shown when a block does not offer it;
// - the use statements shown or hidden (<span class="code-uses">, see bin/dev/highlight.py), hidden by default.
// The choices are saved in the localStorage and apply to every block of every page.
(() => {
    const PHP_KEY = 'codebase.php';
    const USES_KEY = 'codebase.uses';
    const root = document.documentElement;
    const style = document.createElement('style');

    const read = (key) => {
        try {
            return localStorage.getItem(key);
        } catch (error) {
            return null;
        }
    };

    const save = (key, value) => {
        try {
            localStorage.setItem(key, value);
        } catch (error) {
            // No storage (private window, blocked site data): the choice lasts until the page is left
        }
    };

    let php = read(PHP_KEY) ?? 'max';

    // Without this style, the first <pre> of a block is shown: the minimum version
    const showPhp = () => {
        if (php === 'min') {
            style.textContent = '';
        } else if (php === 'max') {
            style.textContent = `
                .code-block[data-php-versions] pre.code { display: none; }
                .code-block[data-php-versions] pre.code:last-of-type { display: block; }`;
        } else {
            style.textContent = `
                .code-block[data-php-versions~="${php}"] pre.code:not([data-php~="${php}"]) { display: none; }
                .code-block[data-php-versions~="${php}"] pre.code[data-php~="${php}"] { display: block; }`;
        }
    };

    // Set before the page is drawn, so that the code of another version or hidden statements never show up
    showPhp();
    document.head.append(style);
    root.classList.toggle('uses-hidden', read(USES_KEY) !== 'shown');

    const button = (text, onClick) => {
        const element = document.createElement('button');
        element.type = 'button';
        element.textContent = text;
        element.addEventListener('click', onClick);
        const item = document.createElement('li');
        item.append(element);

        return [element, item];
    };

    document.addEventListener('DOMContentLoaded', () => {
        const menus = [];

        const update = () => {
            const usesHidden = root.classList.contains('uses-hidden');
            for (const {versions, phpButtons, usesButton} of menus) {
                const shown = php === 'max' ? versions.at(-1) : (versions.includes(php) ? php : versions[0]);
                for (const phpButton of phpButtons) {
                    phpButton.setAttribute('aria-pressed', String(phpButton.dataset.version === shown));
                }
                if (usesButton !== null) {
                    usesButton.setAttribute('aria-pressed', String(!usesHidden));
                }
            }
        };

        for (const block of document.querySelectorAll('.code-block')) {
            const meta = block.querySelector('.code-meta');
            const label = meta === null
                ? undefined
                : [...meta.children].find((child) => child.tagName === 'SPAN' && child.textContent.startsWith('PHP '));
            const versions = block.dataset.phpVersions?.split(' ') ?? (label === undefined ? [] : [label.textContent.slice(4)]);
            const hasUses = block.querySelector('.code-uses') !== null;
            if (label === undefined || (versions.length < 2 && !hasUses)) {
                continue;
            }

            const menu = document.createElement('details');
            menu.className = 'code-menu';
            const summary = document.createElement('summary');
            summary.title = 'Display';
            summary.setAttribute('aria-label', 'Display');
            // Cogwheel
            summary.innerHTML = '<svg class="icon" viewBox="0 0 16 16" aria-hidden="true">'
                + '<path d="M12.9 7 14.8 7.2 14.8 8.8 12.9 9 12.2 10.8 13.3 12.2 12.2 13.3 10.8 12.2 9 12.9 8.8 14.8 7.2 14.8 7 12.9 '
                + '5.2 12.2 3.8 13.3 2.7 12.2 3.8 10.8 3.1 9 1.2 8.8 1.2 7.2 3.1 7 3.8 5.2 2.7 3.8 3.8 2.7 5.2 3.8 7 3.1 7.2 1.2 '
                + '8.8 1.2 9 3.1 10.8 3.8 12.2 2.7 13.3 3.8 12.2 5.2Z"/><circle cx="8" cy="8" r="2"/></svg>';
            const list = document.createElement('ul');

            const phpButtons = versions.map((version, index) => {
                const last = index === versions.length - 1;
                const label = last ? `Max (PHP ${version})` : (index === 0 ? `Min (PHP ${version})` : `PHP ${version}`);
                const [phpButton, item] = button(label, () => {
                    php = last ? 'max' : (index === 0 ? 'min' : version);
                    save(PHP_KEY, php);
                    showPhp();
                    update();
                    menu.open = false;
                });
                phpButton.dataset.version = version;
                list.append(item);

                return phpButton;
            });

            let usesButton = null;
            if (hasUses) {
                const [element, item] = button('use statements', () => {
                    save(USES_KEY, root.classList.toggle('uses-hidden') ? 'hidden' : 'shown');
                    update();
                    menu.open = false;
                });
                item.className = 'code-menu-separated';
                list.append(item);
                usesButton = element;
            }

            menu.append(summary, list);
            label.remove();
            meta.prepend(menu);
            menus.push({versions, phpButtons, usesButton});
        }

        update();
    });
})();
