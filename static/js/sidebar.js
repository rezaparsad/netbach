let items = document.querySelectorAll(".dashboard-menu-items-list")

        function selectActiveDashboardItem() {
            let url = document.URL.split("/")
            let hostname = document.location.host
            if (hostname.includes('127.0.0.1:8002')) {
                hostname = 'panel.netbach.com';
            }
            let lastPart = url[url.length - 2];
            let firstPart = url[3];
            items.forEach(item => {
                item.classList.remove("dashboard-menu-items")
            })
            if (lastPart === "profile") {
                items[1].classList.add("dashboard-menu-items")
            } else if (lastPart === "increase-credit") {
                items[3].classList.add("dashboard-menu-items")
            } else if (lastPart === "transactions") {
                items[4].classList.add("dashboard-menu-items")
            } else if (lastPart === "invoices") {
                items[5].classList.add("dashboard-menu-items")
            } else if (lastPart === "list" && url[url.length - 3] === "ticket") {
                items[6].classList.add("dashboard-menu-items")
            } else if (lastPart === "login-history") {
                items[7].classList.add("dashboard-menu-items")
            } else if (firstPart === 'cloud') {
                items[2].classList.add("dashboard-menu-items")
            } else {
                items[0].classList.add("dashboard-menu-items")
            }
        }

        selectActiveDashboardItem()

        let sidebar = document.querySelector("#sidebar");

        function openNav() {
            sidebar.classList.remove("close-sidebar")
        }

        closeSideBar = () => {
            sidebar.classList.add("close-sidebar")
        }