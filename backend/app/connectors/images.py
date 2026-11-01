"""Reviewed image references; product discovery remains entirely automatic.

No broad 'all government images are free' assumption. Add entries only after
matching the actual publication and reviewing ownership/usage on official pages.
"""
REVIEWED_IMAGES = {
    'https://store.usgs.gov/product/208284': dict(
        image_url='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/vhp_img1052.jpg',
        image_credit='USGS · Meyers y Driedger (2008)',
        image_license='Public domain',
        image_license_url='https://www.usgs.gov/media/images/eruptions-cascade-range-during-past-4000-years-usgs-gip-64'),
    'https://store.usgs.gov/product/208285': dict(
        image_url='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/vhp_img1109.jpg',
        image_credit='USGS · Geologic hazards at volcanoes (GIP 64)',
        image_license='USGS government publication',
        image_license_url='https://pubs.usgs.gov/publication/gip64'),
}


def enrich_image(offer):
    reviewed = REVIEWED_IMAGES.get(offer['url'])
    if reviewed:
        offer.update(reviewed)
        offer['evidence']=[dict(e) for e in offer.get('evidence',[]) if e.get('field')!='image_license']
        offer['evidence'].append(dict(
            field='image_license', source=reviewed['image_license_url'],
            checked_at='2026-11-01T19:41:40.931085+00:00', method='editorial_rights_review',
            note='Imagen oficial del póster. Referencia y derechos revisados; no acredita stock ni envío.'))
    return offer
