/**
 * HTML Include System
 * 
 * This function dynamically loads HTML content from external files and injects them
 * into elements with the "include" class. This allows for modular HTML components
 * like headers, footers, and navigation bars that can be reused across pages.
 * 
 * Usage:
 * <div class="include" url="navbar.html"></div>
 * <div class="include" url="footer.html"></div>
 * 
 * Result: The content of navbar.html and footer.html will be loaded and inserted
 * into these div elements before the page content is displayed.
 * 
 * @param class_name - The CSS class name to search for (default: "include")
 * @param href_attr - The attribute name containing the URL (default: "href")
 * @returns Promise that resolves when all HTML includes are loaded
 */
async function includeHTML(class_name: string = "include", href_attr: string = "href"): Promise<void> {
    // Find all elements that need to include external HTML content
    const elements: HTMLCollectionOf<Element> = document.getElementsByClassName(class_name);
    const promises: Promise<Response>[] = [];
    
    // Create an array of fetch promises for all include requests
    for (let i = 0; i < elements.length; i++) {
        const element: Element = elements[i];
        const url: string | null = element.getAttribute(href_attr);
        if (url) {
            promises.push(fetch(url));
        }
    }
    
    // Wait for all HTML files to be fetched simultaneously
    const responses: Response[] = await Promise.all(promises);
    
    // Inject the fetched HTML content into the corresponding elements
    for (let i = 0; i < elements.length; i++) {
        const element: Element = elements[i];
        element.innerHTML = await responses[i].text();
    }
}

/**
 * Navigation Tab Highlighting System
 * 
 * This function highlights the currently active navigation tab by applying
 * special styling to indicate which page the user is currently viewing.
 * 
 * Usage:
 * <div id="highlight" navbar_elem_id="home"></div>
 * 
 * Result: The navbar item with id "home" will be highlighted with a special
 * background color, text color, and shadow to show it's the active page.
 * 
 * @param highlight_id - The ID of the highlight element (default: "highlight")
 * @param highlight_attr - The attribute name containing the tab ID (default: "navbar_elem_id")
 * @returns Promise that resolves when highlighting is complete
 */
async function highlightTab(highlight_id: string = "highlight", highlight_attr: string = "navbar_elem_id"): Promise<void> {
    // Look for the highlight element that specifies which tab should be active
    const highlighter: HTMLElement | null = document.getElementById(highlight_id);
    if (highlighter === null) {
        return; // No highlight element found, just continue
    }
    
    // Get the ID of the tab that should be highlighted
    const elementId: string | null = highlighter.getAttribute(highlight_attr);
    if (elementId === null) {
        return; // No highlight_id attribute, just continue
    }
    
    // Find the navbar item that should be highlighted
    const navItem: HTMLElement | null = document.getElementById(elementId);
    if (navItem === null) {
        return; // Navbar item not found, just continue
    }
    
    // Apply highlight styling using CSS variables for consistency
    navItem.style.color = "var(--text-light)";                    // Bright white text
    navItem.style.background = "rgba(236, 240, 241, 0.15)";      // Semi-transparent background
    navItem.style.boxShadow = "var(--shadow-light)";              // Subtle shadow for depth
}

/**
 * Dropdown Menu Behavior Management
 * 
 * This function handles the interactive behavior of dropdown menus, providing
 * different experiences for desktop (hover) and mobile (click) users.
 * 
 * Desktop: Dropdowns appear on hover with smooth animations
 * Mobile: Dropdowns toggle on click and stack vertically
 * 
 * @returns Promise that resolves when dropdown behaviors are set up
 */
async function setupDropdownBehavior(): Promise<void> {
    const dropdowns: HTMLCollectionOf<Element> = document.getElementsByClassName('dropdown');
    
    for (let i = 0; i < dropdowns.length; i++) {
        const dropdown: Element = dropdowns[i];
        const dropdownMenu: Element | undefined = dropdown.getElementsByClassName('dropdown-menu')[0];
        const dropdownToggle: Element | undefined = dropdown.getElementsByClassName('dropdown-toggle')[0];
        
        if (dropdownMenu && dropdownToggle) {
            // Desktop behavior: Show dropdown on hover with smooth animations
            if (window.innerWidth > 768) {
                dropdown.addEventListener('mouseenter', function(): void {
                    // Animate dropdown into view
                    (dropdownMenu as HTMLElement).style.opacity = '1';
                    (dropdownMenu as HTMLElement).style.visibility = 'visible';
                    (dropdownMenu as HTMLElement).style.transform = 'translateY(0)';
                });
                
                dropdown.addEventListener('mouseleave', function(): void {
                    // Animate dropdown out of view
                    (dropdownMenu as HTMLElement).style.opacity = '0';
                    (dropdownMenu as HTMLElement).style.visibility = 'hidden';
                    (dropdownMenu as HTMLElement).style.transform = 'translateY(-10px)';
                });
            }
            
            // Mobile behavior: Toggle dropdown on click
            dropdownToggle.addEventListener('click', function(e: Event): void {
                if (window.innerWidth <= 768) {
                    e.preventDefault(); // Prevent navigation on mobile
                    dropdown.classList.toggle('active');
                    
                    // Toggle dropdown visibility for mobile layout
                    if (dropdown.classList.contains('active')) {
                        (dropdownMenu as HTMLElement).style.display = 'block';
                    } else {
                        (dropdownMenu as HTMLElement).style.display = 'none';
                    }
                }
            });
        }
    }
}

/**
 * Mobile Menu System
 * 
 * This function manages the mobile hamburger menu, including:
 * - Toggle button functionality
 * - Menu slide animations
 * - Click-outside-to-close behavior
 * - Responsive state management
 * - Dropdown reset on desktop resize
 * 
 * @returns Promise that resolves when mobile menu is set up
 */
async function setupMobileMenu(): Promise<void> {
    const mobileToggle: Element | undefined = document.getElementsByClassName('mobile-menu-toggle')[0];
    const navMenu: Element | undefined = document.getElementsByClassName('nav-menu')[0];
    const dropdowns: HTMLCollectionOf<Element> = document.getElementsByClassName('dropdown');

    if (mobileToggle && navMenu) {
        // Toggle mobile menu when hamburger button is clicked
        mobileToggle.addEventListener('click', function(): void {
            mobileToggle.classList.toggle('active');  // Animate hamburger to X
            navMenu.classList.toggle('active');       // Toggle menu visibility
            
            // Control the slide animation position
            if (navMenu.classList.contains('active')) {
                (navMenu as HTMLElement).style.top = 'var(--navbar-height)';  // Slide down to show
            } else {
                (navMenu as HTMLElement).style.top = '-100vh';                // Slide up to hide
            }
        });
    }

    // Close mobile menu when clicking outside the navbar
    document.addEventListener('click', function(e: Event): void {
        const target = e.target as Element;
        if (!target.closest('.navbar')) {
            // Reset mobile menu state
            if (mobileToggle) mobileToggle.classList.remove('active');
            if (navMenu) {
                navMenu.classList.remove('active');
                (navMenu as HTMLElement).style.top = '-100vh';  // Hide menu
            }
            
            // Reset all dropdown states
            for (let i = 0; i < dropdowns.length; i++) {
                const dropdown: Element = dropdowns[i];
                dropdown.classList.remove('active');
                const dropdownMenu: Element | undefined = dropdown.getElementsByClassName('dropdown-menu')[0];
                if (dropdownMenu) (dropdownMenu as HTMLElement).style.display = 'none';
            }
        }
    });

    // Handle window resize events
    window.addEventListener('resize', function(): void {
        if (window.innerWidth > 768) {
            // Reset mobile menu state when switching to desktop
            if (mobileToggle) mobileToggle.classList.remove('active');
            if (navMenu) {
                navMenu.classList.remove('active');
                (navMenu as HTMLElement).style.top = '-100vh';
            }
            
            // Reset all dropdown states and restore desktop behavior
            for (let i = 0; i < dropdowns.length; i++) {
                const dropdown: Element = dropdowns[i];
                dropdown.classList.remove('active');
                const dropdownMenu: Element | undefined = dropdown.getElementsByClassName('dropdown-menu')[0];
                if (dropdownMenu) {
                    (dropdownMenu as HTMLElement).style.display = 'none';
                    // Reset transform properties for smooth hover animations
                    (dropdownMenu as HTMLElement).style.opacity = '0';
                    (dropdownMenu as HTMLElement).style.visibility = 'hidden';
                    (dropdownMenu as HTMLElement).style.transform = 'translateY(-10px)';
                }
            }
        }
    });
}

/**
 * Responsive Content Width Management
 * 
 * This function dynamically adjusts the main content width based on screen size,
 * replacing the CSS media queries with JavaScript for more precise control.
 * 
 * Breakpoints:
 * - >1400px: 1200px max-width (large desktop)
 * - >1200px: 1000px max-width (desktop)
 * - >992px:  900px max-width  (tablet landscape)
 * - >768px:  800px max-width  (tablet portrait)
 * - ≤768px:  100% max-width   (mobile)
 * 
 * @returns Promise that resolves when responsive behavior is set up
 */
async function setupResponsiveBehavior(): Promise<void> {
    const mainContent: Element | undefined = document.getElementsByClassName('main-content')[0];
    
    /**
     * Updates the main content width based on current screen size
     */
    function updateContentWidth(): void {
        if (!mainContent) return;
        
        const width: number = window.innerWidth;
        
        // Apply responsive width based on screen size
        if (width > 1400) {
            (mainContent as HTMLElement).style.maxWidth = '1200px';
        } else if (width > 1200) {
            (mainContent as HTMLElement).style.maxWidth = '1000px';
        } else if (width > 992) {
            (mainContent as HTMLElement).style.maxWidth = '900px';
        } else if (width > 768) {
            (mainContent as HTMLElement).style.maxWidth = '800px';
        } else {
            // Mobile: full width with reduced padding
            (mainContent as HTMLElement).style.maxWidth = '100%';
            (mainContent as HTMLElement).style.padding = '15px';
        }
    }
    
    // Set initial width on page load
    updateContentWidth();
    
    // Update width whenever the window is resized
    window.addEventListener('resize', updateContentWidth);
}

/**
 * Navigation Link Hover Effects
 * 
 * This function manages the hover effects for navigation links, providing
 * visual feedback when users hover over menu items on desktop devices.
 * 
 * Note: Hover effects are disabled on mobile to prevent conflicts with
 * touch interactions and improve mobile performance.
 * 
 * @returns Promise that resolves when hover effects are set up
 */
async function setupHoverEffects(): Promise<void> {
    const navMenu: Element | undefined = document.getElementsByClassName('nav-menu')[0];
    if (!navMenu) return;
    
    const navLinks: HTMLCollectionOf<HTMLAnchorElement> = navMenu.getElementsByTagName('a');
    
    for (let i = 0; i < navLinks.length; i++) {
        const link: HTMLAnchorElement = navLinks[i];
        
        // Desktop hover effects
        link.addEventListener('mouseenter', function(): void {
            if (window.innerWidth > 768) {
                link.style.color = 'var(--text-light)';  // Bright white on hover
            }
        });
        
        link.addEventListener('mouseleave', function(): void {
            if (window.innerWidth > 768) {
                link.style.color = 'var(--text-muted)';  // Return to muted gray
            }
        });
    }
}

/**
 * Main Initialization Function
 * 
 * This is the entry point that sets up all the interactive functionality
 * for the website. It runs after the DOM is loaded and HTML includes are processed.
 * 
 * Execution Order:
 * 1. Load external HTML components (navbar, footer) - Must be first
 * 2. Highlight the active navigation tab - Must be after HTML is loaded
 * 3. Set up all interactive behaviors in parallel - Can run simultaneously
 * 
 * Note: Setup functions run in parallel since they don't depend on each other,
 * improving initialization performance.
 * 
 * @returns Promise that resolves when all initialization is complete
 */
async function main(): Promise<void> {
    // Step 1: Load external HTML components (must be first)
    await includeHTML();
    
    // Step 2: Highlight active navigation tab (must be after HTML is loaded)
    await highlightTab();
    
    // Step 3: Set up all interactive behaviors in parallel
    const setupPromises: Promise<void>[] = [
        setupDropdownBehavior(),    // Configure dropdown interactions
        setupMobileMenu(),          // Initialize mobile menu system
        setupResponsiveBehavior(),  // Set up responsive content sizing
        setupHoverEffects()         // Enable navigation hover effects
    ];
    
    // Wait for all setup functions to complete
    await Promise.all(setupPromises);
}

// Start the application when the DOM is ready
main().then(console.log).catch(console.error);
