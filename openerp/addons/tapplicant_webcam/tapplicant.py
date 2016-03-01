from openerp.osv import osv, fields


class tapplicant(osv.osv):
    _inherit = 'tapplicant'

    def action_take_picture(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
 
        res_model, res_id = self.pool.get(
            'ir.model.data').get_object_reference(cr, uid,
                                                  'tapplicant_webcam',
                                                  'action_take_photo_tapplicant')
        dict_act_window = self.pool.get(
            'ir.actions.client').read(cr, uid, res_id, [])
        if not dict_act_window.get('params', False):
            dict_act_window.update({'params': {}})
        dict_act_window['params'].update(
            {'tapplicant_id': len(ids) and ids[0] or False})
        return dict_act_window

    def action_view_picture(self, cr, uid, ids, context=None):
        return {
                  'name'     : 'Picture',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'current',
                  'url'      : "http://c.jobsglobal.com/web/binary/image?model=tapplicant&field=image&filename_field=name&id=" + str(ids[0])
               }