(async () => {
    const usernames = new Set();
    const container = document.querySelector(".scroller__36d07");
    const iteration = 50;

    for (let i = 0; i < iteration; i++) {
        [...document.querySelectorAll('a[href^="https://www.roblox.com/games/"]')].forEach((el) => usernames.add(el.textContent.split(" reviewed ")[0]));
        container.scrollTo(0, 0);
        console.log(`[Risperidone] iteration: ${i}`);

        const ms = 300; // in millisecond; wait for scroll.
        await (new Promise(resolve => setTimeout(resolve, ms)));
    }

    const text = [...usernames].join("\n");
    console.log(text); copy(text);
})();
