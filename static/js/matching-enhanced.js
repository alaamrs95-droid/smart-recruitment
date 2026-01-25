// Enhanced Matching Interface JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('disabled')) {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Loading...';
                this.disabled = true;
                
                // Simulate loading (remove this in production)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 1000);
            }
        });
    });

    // Enhanced match score animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = width;
        }, 100);
    });

    // Add filter functionality
    function addMatchFilters() {
        const tabContent = document.querySelector('#matchTabContent');
        if (tabContent) {
            const filterHtml = `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-search"></i></span>
                            <input type="text" class="form-control" id="searchMatches" placeholder="Search matches...">
                        </div>
                    </div>
                    <div class="col-md-3">
                        <select class="form-control" id="sortBy">
                            <option value="score">Sort by Match Score</option>
                            <option value="date">Sort by Date</option>
                            <option value="name">Sort by Name</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select class="form-control" id="filterBy">
                            <option value="all">All Matches</option>
                            <option value="excellent">Excellent Only</option>
                            <option value="good">Good & Above</option>
                        </select>
                    </div>
                </div>
            `;
            
            // Insert filters before tab content
            tabContent.insertAdjacentHTML('beforebegin', filterHtml);
            
            // Add event listeners
            document.getElementById('searchMatches').addEventListener('input', filterMatches);
            document.getElementById('sortBy').addEventListener('change', sortMatches);
            document.getElementById('filterBy').addEventListener('change', filterMatches);
        }
    }

    // Filter matches function
    function filterMatches() {
        const searchTerm = document.getElementById('searchMatches').value.toLowerCase();
        const filterBy = document.getElementById('filterBy').value;
        const cards = document.querySelectorAll('.match-card');
        
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const scoreElement = card.querySelector('.progress-bar');
            const score = scoreElement ? parseInt(scoreElement.getAttribute('aria-valuenow')) : 0;
            
            let showCard = true;
            
            // Search filter
            if (searchTerm && !text.includes(searchTerm)) {
                showCard = false;
            }
            
            // Score filter
            if (filterBy === 'excellent' && score < 80) {
                showCard = false;
            } else if (filterBy === 'good' && score < 60) {
                showCard = false;
            }
            
            card.parentElement.style.display = showCard ? 'block' : 'none';
        });
    }

    // Sort matches function
    function sortMatches() {
        const sortBy = document.getElementById('sortBy').value;
        const container = document.querySelector('.tab-pane.active .row');
        const cards = Array.from(container.querySelectorAll('.match-card'));
        
        cards.sort((a, b) => {
            if (sortBy === 'score') {
                const scoreA = parseInt(a.querySelector('.progress-bar').getAttribute('aria-valuenow'));
                const scoreB = parseInt(b.querySelector('.progress-bar').getAttribute('aria-valuenow'));
                return scoreB - scoreA;
            } else if (sortBy === 'name') {
                const nameA = a.querySelector('.card-title').textContent.trim();
                const nameB = b.querySelector('.card-title').textContent.trim();
                return nameA.localeCompare(nameB);
            }
            return 0;
        });
        
        // Re-append sorted cards
        cards.forEach(card => container.appendChild(card.parentElement));
    }

    // Initialize filters
    addMatchFilters();

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchMatches');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('searchMatches');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                filterMatches();
            }
        }
    });

    // Add print functionality
    function addPrintButton() {
        const header = document.querySelector('.card-header');
        if (header) {
            const printBtn = document.createElement('button');
            printBtn.className = 'btn btn-sm btn-outline-secondary ml-2';
            printBtn.innerHTML = '<i class="fas fa-print mr-1"></i> Print';
            printBtn.onclick = () => window.print();
            header.querySelector('.card-tools').appendChild(printBtn);
        }
    }

    addPrintButton();

    // Add export functionality
    function addExportButton() {
        const header = document.querySelector('.card-header');
        if (header) {
            const exportBtn = document.createElement('button');
            exportBtn.className = 'btn btn-sm btn-outline-info ml-2';
            exportBtn.innerHTML = '<i class="fas fa-download mr-1"></i> Export';
            exportBtn.onclick = exportMatches;
            header.querySelector('.card-tools').appendChild(exportBtn);
        }
    }

    function exportMatches() {
        const matches = [];
        document.querySelectorAll('.match-card').forEach(card => {
            const title = card.querySelector('.card-title').textContent.trim();
            const score = card.querySelector('.progress-bar').getAttribute('aria-valuenow');
            const reasons = Array.from(card.querySelectorAll('.bg-light .small')).map(el => el.textContent);
            
            matches.push({
                title,
                score,
                reasons
            });
        });
        
        const dataStr = JSON.stringify(matches, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = 'matches_export.json';
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    addExportButton();
});

// Add responsive grid adjustments
function adjustGridForMobile() {
    const cards = document.querySelectorAll('.match-card');
    const isMobile = window.innerWidth < 768;
    
    cards.forEach(card => {
        if (isMobile) {
            card.parentElement.classList.remove('col-md-6', 'col-lg-4');
            card.parentElement.classList.add('col-12');
        } else {
            card.parentElement.classList.remove('col-12');
            card.parentElement.classList.add('col-md-6', 'col-lg-4');
        }
    });
}

window.addEventListener('resize', adjustGridForMobile);
adjustGridForMobile();
