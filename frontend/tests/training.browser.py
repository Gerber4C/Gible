"""Browser check for generated opening/response deals.

Start the frontend on 5173 and the backend on 8765. For testing beside an
already running backend, set GIBLE_TEST_BACKEND_PORT to a fresh backend port.
"""

import os
import re

from playwright.sync_api import sync_playwright, expect


def run():
    port = os.environ.get('GIBLE_TEST_BACKEND_PORT', os.environ.get('PARTNER_TEST_BACKEND_PORT', '8765'))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1500, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        if port != '8765':
            page.route('http://127.0.0.1:8765/**', lambda route:
                       route.continue_(url=route.request.url.replace(':8765/', f':{port}/')))
        page.goto('http://127.0.0.1:5173/')
        page.wait_for_load_state('networkidle')
        page.get_by_role('button', name='Table', exact=True).click()
        expect(page.locator('aside select')).to_have_value('daqiush_2over1')
        page.get_by_label('Training mode').select_option('response')
        expect(page.get_by_label('Training opener')).to_have_value('ns')
        page.get_by_label('Target opening').fill('1NT')
        page.get_by_label('Target response').fill('4C')
        page.get_by_label('Training opener').select_option('e')
        page.get_by_label('Training seed').fill('13')
        page.get_by_role('button', name='Generate matching deal').click()
        expect(page.get_by_text('Matched after', exact=False)).to_be_visible(timeout=15000)
        expect(page.locator('.deal-health')).to_contain_text('Valid deal')
        expect(page.get_by_label('Training opener')).to_have_value('e')
        page.get_by_role('button', name='Show full auction').click()
        expect(page.locator('.auction-center')).to_contain_text('1NT', timeout=15000)
        expect(page.locator('.auction-center')).to_contain_text('4♣')
        page.get_by_label('Training mode').select_option('opening')
        page.get_by_label('Training seed').fill('15')
        for pair, seat_pattern in (('ns', r'[NS]'), ('ew', r'[EW]')):
            page.get_by_label('Training opener').select_option(pair)
            page.get_by_role('button', name='Generate matching deal').click()
            expect(page.get_by_text(re.compile(r'Matched after .* · ' + seat_pattern + r' opens'))).to_be_visible(timeout=15000)
            expect(page.get_by_label('Training opener')).to_have_value(pair)
            expect(page.locator('.deal-health')).to_contain_text('Valid deal')
        assert not errors, errors
        browser.close()


if __name__ == '__main__':
    run()
