async function includeHTML() {
    // for all elements from this site
    // if they have "include-url", that is a html file
    // get that file and replace the element

    // how to use
    // <div class="include" url="navbar.html"></div>
    // content
    // <div class="include" url="footer.html"></div>
    // <script src="js/post_script.js"></script>
    //
    // result: navbar and footer are included before and after content

    const elements = document.getElementsByClassName("include");
    const promises = [];
    for (let i=0; i<elements.length; i++) {
        const element = elements[i];
        const url = element.getAttribute("url");
        promises.push(fetch(url));
    }
    let responses = await Promise.all(promises);
    for (let i=0; i<elements.length; i++) {
        const element = elements[i];
        element.innerHTML = await responses[i].text();
    }
}

async function highlightTab() {
    // highlight a tab name

    // how to use
    // <div id="highlight" highlight_id="about" ></div>
    //
    // result: if there is an element of id "about", its color will change to white

    const highlighter = document.getElementById("highlight");
    if (highlighter === null) {
        throw new Error("Error: there is no element \"highlight\" ");
    }
    const elementId = highlighter.getAttribute("highlight_id");
    if (elementId === null) {
        throw new Error("Error: highlight element has no field \"highlight_id\"")
    }
    const element = document.getElementById(elementId);
    if (element === null) {
        throw new Error(`Error: there is no element \"${elementId}\"`)
    }
    element.style.color = "#ffffff";
}

function setupMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const dropdowns = document.querySelectorAll('.dropdown');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Handle dropdowns on mobile
    dropdowns.forEach(dropdown => {
        const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
        if (dropdownToggle) {
            dropdownToggle.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    dropdown.classList.toggle('active');
                }
            });
        }
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.navbar')) {
            if (mobileToggle) mobileToggle.classList.remove('active');
            if (navMenu) navMenu.classList.remove('active');
            dropdowns.forEach(dropdown => dropdown.classList.remove('active'));
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            if (mobileToggle) mobileToggle.classList.remove('active');
            if (navMenu) navMenu.classList.remove('active');
            dropdowns.forEach(dropdown => dropdown.classList.remove('active'));
        }
    });
}

async function main() {
    await includeHTML();
    await highlightTab();
    setupMobileMenu();
}

main().then(console.log).catch(console.error);
