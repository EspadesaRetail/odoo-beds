
from odoo import models, fields, api, _


class ResPartnerReviewContent(models.Model):
    _name = 'res.partner.review_content'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Shop')
    review_identificator = fields.Char(
        string=_('reviewId'))
    reviewer_profile_photo = fields.Char(
        string=_('profilePhotoUrl'))
    reviewer_displayname = fields.Char(
        string=_('displayName'))
    review_rating = fields.Integer(
        string=_('starRating'))
    review_comment = fields.Text(
        string=_('comment'))
    review_create_time = fields.Datetime(
        string=_('createTime'))
    review_update_time = fields.Datetime(
        string=_('updateTime'))
    reply_comment = fields.Text(
        string=_('reply'))
    reply_update_time = fields.Datetime(
        string=_('reply updateTime'))


class ResPartnerFormat(models.Model):
    _name = 'res.partner.format'

    name = fields.Char(
        string=_('Format Name'),
        required=True,
        translate=True)
    format = fields.Char(
        string=_('Format Sequence'),
        default=_('New'))
    description = fields.Text(
        string='Description',
        translate=True)
    partner_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='format_id',
        string='Shops')
    google_account = fields.Char(
        string=_('AccountId (google)'),
        translate=True)
    image = fields.Binary(
        "Logo",
        attachment=True,
        help="This field holds the image used as logo for the brand, limited to 1024x1024px.")

    @api.model
    def create(self, vals):
        if vals.get('format', _('New')) == _('New'):
            vals['format'] = self.env['ir.sequence'].next_by_code(
                'res.partner.format') or '/'
        return super(ResPartnerFormat, self).create(vals)


class ResPartnerReview(models.Model):
    _name = 'res.partner.review'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Shop')
    date_review = fields.Date(
        string=_('Date'),
        default=fields.Date.context_today,
        required=True)
    review_number = fields.Integer(
        string=_('Number of reviews'),
        required=True)
    review_value = fields.Float(
        sting=_('Value'),
        required=True)
    review_increase = fields.Integer(
        string=_('New reviews'),
        required=True,
        default=0)
    espadesa_shop = fields.Integer(
        string=_('Shop Number'),
        related="partner_id.espadesa_shop",
        readonly=True,
    )

    @api.multi
    @api.onchange('review_number', 'partner_id')
    @api.depends('review_number', 'partner_id')
    def _compute_new_reviews(self):
        for record in self:
            if record.review_number:
                old_review_number = self.search(
                    [('partner_id.id', '=', record.partner_id.id)],
                    limit=1,
                    order='date_review desc')
                if old_review_number.id:
                    record.review_increase = record.review_number - old_review_number.review_number

    @api.model
    def create(self, vals):
        if vals.get('review_number'):
            old_review_number = self.search(
                [('partner_id', '=', vals['partner_id'])],
                limit=1,
                order='date_review desc')
            if old_review_number.id:
                vals['review_increase'] = vals['review_number'] - old_review_number.review_number
            else:
                vals['review_increase'] = vals['review_number']
        return super(ResPartnerReview, self).create(vals)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    format = fields.Selection(
        selection='_list_all_formats',
        string='Shop Format')
    format_id = fields.Many2one(
        comodel_name='res.partner.format',
        string='Linked to Shop Format')
    review_ids = fields.One2many(
        comodel_name='res.partner.review',
        inverse_name='partner_id',
        string='Review')
    espadesa_shop = fields.Integer(
        string=_('Shop Number'))
    google_location = fields.Char(
        string=_('LocationId (google)'),
        translate=True)

    @api.model
    def _list_all_formats(self):
        self._cr.execute("SELECT format, name FROM res_partner_format ORDER BY format")
        return self._cr.fetchall()

    @api.onchange('format')
    def _onchange_format(self):
        if self.format:
            domain = [('format', '=', self.format)]
            self.format_id = self.env['res.partner.format'].sudo().search(domain)
        else:
            self.format_id = None
