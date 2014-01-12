window.ParsleyConfig ?= {}
window.settlers ?= {}
window.settlers.parsley_validators ?= {}

window.settlers.parsley_validators.expand_constraints = (constraints) ->
  if constraints
    return constraints.split(',')
  return null

window.settlers.parsley_validators.init = ($) ->
  window.ParsleyConfig = $.extend true, {}, window.ParsleyConfig,
    validators:
      filedimensionsmax: () ->
        return {
          validate: (val, constraints, field) ->
            constraints = window.settlers.parsley_validators.expand_constraints constraints

            if $(constraints[0])[0].naturalWidth <= constraints[1] and $(constraints[0])[0].naturalHeight <= constraints[2]
              return true

            return false
        }

      filedimensionsmin: () ->
        return {
          validate: (val, constraints, field) ->
            constraints = window.settlers.parsley_validators.expand_constraints constraints

            if $(constraints[0])[0].naturalWidth >= constraints[1] and $(constraints[0])[0].naturalHeight >= constraints[2]
              return true

            return false
        }

      filesize: () ->
        return {
          validate: (val, limit, field) ->
            limit = Number limit

            file = field.$element[0].files[0]
            if not file
              return true

            if file.size <= limit
              return true

            return false
        }

      filetype: () ->
        return {
          validate: (val, constraints, field) ->
            file = field.$element[0].files[0]
            if not file
              return true

            if constraints.indexOf(file.type) >= 0
              return true

            return false
        }

    messages:
      filedimensionsmax: 'Image is bigger than allowed'
      filedimensionsmin: 'Image is smaller than required'
      filesize: 'Image is bigger than allowed'

window.settlers.parsley_validators.init(window.jQuery || window.Zepto)
