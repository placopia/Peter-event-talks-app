// Global state
let state = {
    releases: [],
    selectedCategory: 'all',
    searchQuery: '',
    selectedReleaseId: null,
    isLoading: false
};

// DOM Elements
const feedContainer = document.getElementById('feed-container');
const searchInput = document.getElementById('search-input');
const categoryFilters = document.getElementById('category-filters');
const statTotalCount = document.getElementById('stat-total-count');
const statLastSync = document.getElementById('stat-last-sync');
const btnRefresh = document.getElementById('btn-refresh');
const refreshSpinner = document.getElementById('refresh-spinner');
const errorBanner = document.getElementById('error-banner');
const errorMessage = document.getElementById('error-message');
const btnCloseError = document.getElementById('btn-close-error');

// Composer Drawer Elements
const composerDrawer = document.getElementById('composer-drawer');
const composerEmptyState = document.getElementById('composer-empty-state');
const composerContent = document.getElementById('composer-content');
const btnCloseDrawer = document.getElementById('btn-close-drawer');
const previewBadge = document.getElementById('preview-badge');
const previewDate = document.getElementById('preview-date');
const previewText = document.getElementById('preview-text');
const tweetTextarea = document.getElementById('tweet-textarea');
const charCountText = document.getElementById('char-count-text');
const charProgress = document.getElementById('char-progress');
const btnSendTweet = document.getElementById('btn-send-tweet');

// Category Counts Elements
const countAll = document.getElementById('count-all');
const countFeature = document.getElementById('count-feature');
const countChange = document.getElementById('count-change');
const countIssue = document.getElementById('count-issue');
const countDeprecation = document.getElementById('count-deprecation');
const countGeneral = document.getElementById('count-general');

// SVG Circular progress details
const CIRCLE_RADIUS = 14;
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS; // ~87.96

// Setup Progress Ring
if (charProgress) {
    charProgress.style.strokeDasharray = `${CIRCLE_CIRCUMFERENCE} ${CIRCLE_CIRCUMFERENCE}`;
    charProgress.style.strokeDashoffset = CIRCLE_CIRCUMFERENCE;
}

// Initial initialization
document.addEventListener('DOMContentLoaded', () => {
    fetchReleases();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search input
    searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value.toLowerCase();
        renderFeed();
    });

    // Category filter clicks
    categoryFilters.addEventListener('click', (e) => {
        const button = e.target.closest('.filter-btn');
        if (!button) return;

        // Update active class
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        state.selectedCategory = button.dataset.category;
        renderFeed();
    });

    // Refresh sync button
    btnRefresh.addEventListener('click', () => {
        fetchReleases(true);
    });

    // Close error banner
    btnCloseError.addEventListener('click', () => {
        errorBanner.classList.add('hidden');
    });

    // Close composer drawer (relevant on mobile/tablets)
    btnCloseDrawer.addEventListener('click', () => {
        composerDrawer.classList.remove('drawer-open');
    });

    // Tweet textarea typing
    tweetTextarea.addEventListener('input', () => {
        updateCharCounter();
    });

    // Send tweet button click
    btnSendTweet.addEventListener('click', () => {
        const text = tweetTextarea.value;
        if (!text || text.length > 280) return;

        // Twitter Share Intent
        const twitterIntentUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(twitterIntentUrl, '_blank', 'noopener,noreferrer,width=550,height=420');
    });
}

// Fetch releases from Flask API
async function fetchReleases(force = false) {
    if (state.isLoading) return;
    
    setLoadingState(true);
    errorBanner.classList.add('hidden');
    
    try {
        const response = await fetch(`/api/releases${force ? '?refresh=true' : ''}`);
        if (!response.ok) {
            throw new Error(`Failed to retrieve release notes: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        state.releases = data.releases || [];
        
        // Update stats
        statTotalCount.textContent = state.releases.length;
        statLastSync.textContent = data.last_updated || 'Just now';
        
        // Update counts
        updateCategoryCounts();
        
        // Render
        renderFeed();
        
    } catch (err) {
        console.error(err);
        showError(err.message || 'An error occurred while fetching updates. Please check your network.');
    } finally {
        setLoadingState(false);
    }
}

// Set Loading Spinner and Cards
function setLoadingState(isLoading) {
    state.isLoading = isLoading;
    if (isLoading) {
        btnRefresh.disabled = true;
        refreshSpinner.classList.add('spinning');
        renderSkeletons();
    } else {
        btnRefresh.disabled = false;
        refreshSpinner.classList.remove('spinning');
    }
}

// Show Error Banner
function showError(message) {
    errorMessage.textContent = message;
    errorBanner.classList.remove('hidden');
}

// Update Counts for categories dynamically
function updateCategoryCounts() {
    const counts = {
        all: state.releases.length,
        Feature: 0,
        Change: 0,
        Issue: 0,
        Deprecation: 0,
        General: 0
    };
    
    state.releases.forEach(rel => {
        const cat = rel.category;
        if (counts.hasOwnProperty(cat)) {
            counts[cat]++;
        } else {
            counts.General++;
        }
    });
    
    countAll.textContent = counts.all;
    countFeature.textContent = counts.Feature;
    countChange.textContent = counts.Change;
    countIssue.textContent = counts.Issue;
    countDeprecation.textContent = counts.Deprecation;
    countGeneral.textContent = counts.General;
}

// Render Skeletons during Loading
function renderSkeletons() {
    feedContainer.innerHTML = '';
    for (let i = 0; i < 4; i++) {
        const skel = document.createElement('div');
        skel.className = 'skeleton-card';
        skel.innerHTML = `
            <div style="display: flex; justify-content: space-between;">
                <div class="skeleton-shimmer sk-badge"></div>
                <div class="skeleton-shimmer sk-date"></div>
            </div>
            <div class="skeleton-shimmer sk-line-1" style="margin-top: 10px;"></div>
            <div class="skeleton-shimmer sk-line-2"></div>
            <div class="skeleton-shimmer sk-line-3"></div>
        `;
        feedContainer.appendChild(skel);
    }
}

// Filter and Render Feed Cards
function renderFeed() {
    if (state.isLoading) return;
    
    feedContainer.innerHTML = '';
    
    const filtered = state.releases.filter(rel => {
        // Category Filter
        const matchesCategory = state.selectedCategory === 'all' || rel.category === state.selectedCategory;
        
        // Search Filter
        const matchesSearch = !state.searchQuery || 
                              rel.content_text.toLowerCase().includes(state.searchQuery) ||
                              rel.category.toLowerCase().includes(state.searchQuery) ||
                              rel.date.toLowerCase().includes(state.searchQuery);
                              
        return matchesCategory && matchesSearch;
    });
    
    if (filtered.length === 0) {
        feedContainer.innerHTML = `
            <div class="no-results animate-fade-in">
                <i class="fa-solid fa-folder-open"></i>
                <h3>No release notes match your filters</h3>
                <p>Try searching for a different keyword or category.</p>
            </div>
        `;
        return;
    }
    
    filtered.forEach(rel => {
        const card = document.createElement('div');
        card.className = `update-card card-${rel.category.toLowerCase()} animate-fade-in`;
        card.dataset.id = rel.id;
        
        if (state.selectedReleaseId === rel.id) {
            card.classList.add('selected');
        }
        
        card.innerHTML = `
            <div class="card-header">
                <div class="card-meta-left">
                    <span class="category-badge badge-${rel.category.toLowerCase()}">${rel.category}</span>
                    <span class="card-date"><i class="fa-regular fa-calendar-days"></i> ${rel.date}</span>
                </div>
                <div class="card-tweet-indicator" title="Select to draft Tweet">
                    <i class="fa-brands fa-x-twitter"></i>
                </div>
            </div>
            <div class="card-body">
                ${rel.content_html}
            </div>
            <div class="card-footer">
                <span class="tweet-action-link">
                    <i class="fa-solid fa-pen-nib"></i>
                    <span>Draft Tweet</span>
                </span>
            </div>
        `;
        
        card.addEventListener('click', () => {
            selectRelease(rel.id);
        });
        
        feedContainer.appendChild(card);
    });
}

// Select a release card
function selectRelease(id) {
    state.selectedReleaseId = id;
    
    // Toggle card selection visually
    document.querySelectorAll('.update-card').forEach(card => {
        if (card.dataset.id === id) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    const release = state.releases.find(rel => rel.id === id);
    if (!release) return;
    
    // Update Composer Drawer
    previewBadge.className = `preview-badge badge-${release.category.toLowerCase()}`;
    previewBadge.textContent = release.category;
    previewDate.textContent = release.date;
    previewText.innerHTML = release.content_html;
    
    // Populate textarea with pre-generated tweet suggestion
    tweetTextarea.value = release.suggested_tweet;
    
    // Switch states
    composerEmptyState.classList.add('hidden');
    composerContent.classList.remove('hidden');
    
    // Calculate character counters
    updateCharCounter();
    
    // For responsive views, open drawer as sheet overlay
    composerDrawer.classList.add('drawer-open');
}

// Update Twitter circular progress bar and counter
function updateCharCounter() {
    const text = tweetTextarea.value;
    const count = text.length;
    const remaining = 280 - count;
    
    charCountText.textContent = remaining;
    
    // CSS classes based on limits
    charCountText.className = 'char-count';
    if (remaining < 0) {
        charCountText.classList.add('danger');
        btnSendTweet.disabled = true;
    } else if (remaining <= 40) {
        charCountText.classList.add('warning');
        btnSendTweet.disabled = false;
    } else {
        btnSendTweet.disabled = false;
    }
    
    if (count === 0) {
        btnSendTweet.disabled = true;
    }
    
    // Circular SVG progress bar
    if (charProgress) {
        // Bound percentages between 0 and 100
        const percentage = Math.min(100, (count / 280) * 100);
        const offset = CIRCLE_CIRCUMFERENCE - (percentage / 100) * CIRCLE_CIRCUMFERENCE;
        charProgress.style.strokeDashoffset = offset;
        
        // Color transition
        if (remaining < 0) {
            charProgress.style.stroke = 'var(--color-deprecation)';
        } else if (remaining <= 40) {
            charProgress.style.stroke = 'var(--color-issue)';
        } else {
            charProgress.style.stroke = 'var(--color-primary)';
        }
    }
}
