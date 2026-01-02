$(document).ready(function () {

    // Data Tables
    // Enhanced Users Table with search and export
    if ($('#user-table').length && !$.fn.DataTable.isDataTable('#user-table')) {
        var userTable = $('#user-table').DataTable({
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            responsive: true,
            "order": [[1, "desc"]],
            dom: 'Brtip',
            buttons: [
                {
                    extend: 'copyHtml5',
                    text: '<span class="icon-ui-copy"></span> Copy',
                    className: 'btn btn-clear'
                },
                {
                    extend: 'excelHtml5',
                    text: '<span class="icon-ui-download"></span> Excel',
                    className: 'btn btn-clear',
                    filename: 'users_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'csvHtml5',
                    text: '<span class="icon-ui-download"></span> CSV',
                    className: 'btn btn-clear',
                    filename: 'users_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'pdfHtml5',
                    text: '<span class="icon-ui-download"></span> PDF',
                    className: 'btn btn-clear',
                    filename: 'users_export_' + new Date().toISOString().split('T')[0],
                    orientation: 'landscape',
                    pageSize: 'A4'
                }
            ],
            "language": {
                "search": "",
                "searchPlaceholder": "Search users..."
            }
        });

        // Enhanced search input
        $('#user-search-input').on('keyup', function() {
            userTable.search(this.value).draw();
        });

        // Filter buttons
        $('.js-filter-btn').on('click', function() {
            var filter = $(this).data('filter');
            $('.js-filter-btn').removeClass('is-active');
            $(this).addClass('is-active');
            
            if (filter === 'all') {
                userTable.column(3).search('').draw();
            } else if (filter === 'active') {
                userTable.column(3).search('^Active$', true, false).draw();
            } else if (filter === 'inactive') {
                userTable.column(3).search('^Inactive$', true, false).draw();
            }
        });

        // Set default filter to "All"
        $('.js-filter-btn[data-filter="all"]').addClass('is-active');

        // Clickable rows
        $('#user-table tbody').on('click', 'tr', function () {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
            } else {
                userTable.$('tr.selected').removeClass('selected');
                $(this).addClass('selected');
            }
            window.location = $(this).data("href");
        });
    }

    // Note: ws-table is now initialized below with enhanced features (search, filter, export)

    $('#server-history').DataTable({
        "pageLength": 25,
        responsive: true,
        "order": [[0, "desc"]],
        dom: 'lBfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    $('#product-users').DataTable({
        "pageLength": 25,
        responsive: true,
        "order": [[0, "desc"]],
        dom: 'lBfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    $('#user-products').DataTable({
        "pageLength": 25,
        responsive: true,
        "order": [[0, "desc"]],
        dom: 'lBfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    $('#ws-products').DataTable({
        "pageLength": 25,
        responsive: true,
        "order": [[0, "desc"]],
        dom: 'lBfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    $('#server-users-table').DataTable({
        "pageLength": 7,
        responsive: true,
        "order": [[0, "desc"]],
        dom: 'lBfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    // Products Table with search and export
    if ($('#products-table').length && !$.fn.DataTable.isDataTable('#products-table')) {
        var productsTable = $('#products-table').DataTable({
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            responsive: true,
            "order": [[0, "asc"]],
            dom: 'Brtip',
            buttons: [
                {
                    extend: 'copyHtml5',
                    text: '<span class="icon-ui-copy"></span> Copy',
                    className: 'btn btn-clear'
                },
                {
                    extend: 'excelHtml5',
                    text: '<span class="icon-ui-download"></span> Excel',
                    className: 'btn btn-clear',
                    filename: 'products_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'csvHtml5',
                    text: '<span class="icon-ui-download"></span> CSV',
                    className: 'btn btn-clear',
                    filename: 'products_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'pdfHtml5',
                    text: '<span class="icon-ui-download"></span> PDF',
                    className: 'btn btn-clear',
                    filename: 'products_export_' + new Date().toISOString().split('T')[0],
                    orientation: 'landscape',
                    pageSize: 'A4'
                }
            ],
            "language": {
                "search": "",
                "searchPlaceholder": "Search products..."
            }
        });

        $('#products-search-input').on('keyup', function() {
            productsTable.search(this.value).draw();
        });

        $('.js-filter-btn').on('click', function() {
            var filter = $(this).data('filter');
            $('.js-filter-btn').removeClass('is-active');
            $(this).addClass('is-active');
            
            if (filter === 'all') {
                productsTable.column(5).search('').draw();
            } else if (filter === 'available') {
                productsTable.column(5).search('^Available$', true, false).draw();
            } else if (filter === 'full') {
                productsTable.column(5).search('^Full$', true, false).draw();
            }
        });

        $('.js-filter-btn[data-filter="all"]').addClass('is-active');

        $('#products-table tbody').on('click', 'tr', function () {
            window.location = $(this).data("href");
        });
    }

    // Workstations Table with search and export
    if ($('#ws-table').length && !$.fn.DataTable.isDataTable('#ws-table')) {
        var wsTable = $('#ws-table').DataTable({
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            responsive: true,
            "order": [[1, "desc"]],
            dom: 'Brtip',
            buttons: [
                {
                    extend: 'copyHtml5',
                    text: '<span class="icon-ui-copy"></span> Copy',
                    className: 'btn btn-clear'
                },
                {
                    extend: 'excelHtml5',
                    text: '<span class="icon-ui-download"></span> Excel',
                    className: 'btn btn-clear',
                    filename: 'workstations_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'csvHtml5',
                    text: '<span class="icon-ui-download"></span> CSV',
                    className: 'btn btn-clear',
                    filename: 'workstations_export_' + new Date().toISOString().split('T')[0]
                },
                {
                    extend: 'pdfHtml5',
                    text: '<span class="icon-ui-download"></span> PDF',
                    className: 'btn btn-clear',
                    filename: 'workstations_export_' + new Date().toISOString().split('T')[0],
                    orientation: 'landscape',
                    pageSize: 'A4'
                }
            ],
            "language": {
                "search": "",
                "searchPlaceholder": "Search workstations..."
            }
        });

        $('#ws-search-input').on('keyup', function() {
            wsTable.search(this.value).draw();
        });

        $('.js-filter-btn').on('click', function() {
            var filter = $(this).data('filter');
            $('.js-filter-btn').removeClass('is-active');
            $(this).addClass('is-active');
            
            if (filter === 'all') {
                wsTable.column(3).search('').draw();
            } else if (filter === 'active') {
                wsTable.column(3).search('^Active$', true, false).draw();
            } else if (filter === 'inactive') {
                wsTable.column(3).search('^Inactive$', true, false).draw();
            }
        });

        $('.js-filter-btn[data-filter="all"]').addClass('is-active');

        $('#ws-table tbody').on('click', 'tr', function () {
            window.location = $(this).data("href");
        });
    }

    // Servers search and filter
    var $searchInput = $('#servers-search-input');
    var $serverCards = $('.server-card');
    var currentFilter = 'all';

    if ($searchInput.length && $serverCards.length) {
        function filterServers() {
            var searchTerm = $searchInput.val().toLowerCase();
            
            $serverCards.each(function() {
                var $card = $(this);
                var serverName = $card.data('servername') || '';
                var status = $card.data('status') || '';
                var matchesSearch = serverName.includes(searchTerm);
                var matchesFilter = true;
                
                if (currentFilter === 'up') {
                    matchesFilter = status === 'up';
                } else if (currentFilter === 'down') {
                    matchesFilter = status !== 'up';
                }
                
                if (matchesSearch && matchesFilter) {
                    $card.removeClass('hidden');
                } else {
                    $card.addClass('hidden');
                }
            });
        }

        $searchInput.on('keyup', filterServers);

        $('.js-filter-btn').on('click', function() {
            var filter = $(this).data('filter');
            $('.js-filter-btn').removeClass('is-active');
            $(this).addClass('is-active');
            currentFilter = filter;
            filterServers();
        });

        $('.js-filter-btn[data-filter="all"]').addClass('is-active');
    }

    //Sortable tables
    $("#user-workstation").stupidtable();
    $("#user-server").stupidtable();
    $("#ws-workstation").stupidtable();
    $("#ws-server").stupidtable();

    $(".request-btn").on("click", function(){
        console.log(this)
    })


});




