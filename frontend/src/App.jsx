import { useState, useEffect, useMemo } from 'react'
import ProtectedRoute from './auth/ProtectedRoute'
import { useAuth } from './auth/AuthContext'
import API, { apiFetch, isAdmin } from './api/client'

function formatTime(timeStr) {
  if (!timeStr) return ''
  const [h, m] = timeStr.split(':')
  return `${h}:${m}`
}

const CATEGORIAS = ['tecnica', 'pies', 'sparring', 'acondicionamiento', 'defensa', 'cardio', 'otro']
const DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
const NIVELES = ['principiante', 'intermedio', 'avanzado']

const CATEGORIAS_ICONOS = {
  tecnica: '🥊',
  pies: '👣',
  defensa: '🛡️',
  sparring: '🤼',
  acondicionamiento: '🏃',
  cardio: '💓',
  otro: '📦',
}

const CATEGORIAS_COLORES = {
  tecnica: 'bg-red-900/40 text-red-300 border-red-700',
  pies: 'bg-emerald-900/40 text-emerald-300 border-emerald-700',
  defensa: 'bg-blue-900/40 text-blue-300 border-blue-700',
  sparring: 'bg-orange-900/40 text-orange-300 border-orange-700',
  acondicionamiento: 'bg-yellow-900/40 text-yellow-300 border-yellow-700',
  cardio: 'bg-pink-900/40 text-pink-300 border-pink-700',
  otro: 'bg-gray-700 text-gray-300 border-gray-600',
}

function formatDayName(dia) {
  if (!dia) return ''
  const map = {
    lunes: 'Lun', martes: 'Mar', miercoles: 'Mié', jueves: 'Jue',
    viernes: 'Vie', sabado: 'Sáb', domingo: 'Dom'
  }
  return map[dia] || dia
}

function App() {
  const { currentUser, logout, token } = useAuth()
  const [tab, setTab] = useState('asistencia')
  const [alumnos, setAlumnos] = useState([])
  const [entrenadores, setEntrenadores] = useState([])
  const [horarios, setHorarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState('')

  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0])
  const [horarioId, setHorarioId] = useState(null)
  const [search, setSearch] = useState('')
  const [selectedAlumno, setSelectedAlumno] = useState(null)
  const [selectedEntrenadorIds, setSelectedEntrenadorIds] = useState([])
  const [asistenciasHoy, setAsistenciasHoy] = useState([])
  const [showNuevoAlumno, setShowNuevoAlumno] = useState(false)
  const [nuevoNombre, setNuevoNombre] = useState('')
  const [nuevoTelefono, setNuevoTelefono] = useState('')
  const [nuevoEntrenadorId, setNuevoEntrenadorId] = useState('')

  const [reporteDesde, setReporteDesde] = useState('')
  const [reporteHasta, setReporteHasta] = useState('')
  const [reporte, setReporte] = useState(null)
  const [seguimiento, setSeguimiento] = useState([])
  const [cobertura, setCobertura] = useState([])
  const [carga, setCarga] = useState([])
  const [porHorario, setPorHorario] = useState([])
  const [cumplimiento, setCumplimiento] = useState([])

  const [editingAlumnoKey, setEditingAlumnoKey] = useState(null)
  const [editEntrenadorIds, setEditEntrenadorIds] = useState([])
  const [deleteConfirmKey, setDeleteConfirmKey] = useState(null)

  const [entrenamientos, setEntrenamientos] = useState([])
  const [filtroCategoria, setFiltroCategoria] = useState('')
  const [filtroDia, setFiltroDia] = useState('')
  const [busquedaEntrenamiento, setBusquedaEntrenamiento] = useState('')
  const [vistaEntrenamientos, setVistaEntrenamientos] = useState('grid')
  const [loadingEntrenamientos, setLoadingEntrenamientos] = useState(false)
  const [showModalEntrenamiento, setShowModalEntrenamiento] = useState(false)
  const [editingEntrenamiento, setEditingEntrenamiento] = useState(null)
  const [formNombre, setFormNombre] = useState('')
  const [formCategoria, setFormCategoria] = useState('tecnica')
  const [formDia, setFormDia] = useState('')
  const [formDescripcion, setFormDescripcion] = useState('')
  const [formVideoUrl, setFormVideoUrl] = useState('')
  const [formThumbnail, setFormThumbnail] = useState('')
  const [formDuracion, setFormDuracion] = useState('')
  const [formNivel, setFormNivel] = useState('')
  const [formObjetivo, setFormObjetivo] = useState('')
  const [formEquipamiento, setFormEquipamiento] = useState('')
  const [formEjercicios, setFormEjercicios] = useState('')
  const [deleteConfirmEntrenamiento, setDeleteConfirmEntrenamiento] = useState(null)
  const [showDetalleEntrenamiento, setShowDetalleEntrenamiento] = useState(false)
  const [entrenamientoSeleccionado, setEntrenamientoSeleccionado] = useState(null)

  const [profileAlumno, setProfileAlumno] = useState(null)
  const [profileEntrenamientos, setProfileEntrenamientos] = useState([])
  const [showModalAsignar, setShowModalAsignar] = useState(false)
  const [editingAsignacion, setEditingAsignacion] = useState(null)
  const [formEntrenamientoId, setFormEntrenamientoId] = useState('')
  const [formEntrenadorId, setFormEntrenadorId] = useState('')
  const [formFecha, setFormFecha] = useState(new Date().toISOString().split('T')[0])
  const [formEstado, setFormEstado] = useState('planificado')
  const [formNotas, setFormNotas] = useState('')
  const [deleteConfirmAsignacion, setDeleteConfirmAsignacion] = useState(null)

  const [deleteConfirmAlumno, setDeleteConfirmAlumno] = useState(null)
  const [alumnoDeleteStats, setAlumnoDeleteStats] = useState({ asistencias: 0, entrenamientos: 0 })

  const [showDuplicados, setShowDuplicados] = useState(false)
  const [duplicados, setDuplicados] = useState([])
  const [mergePrincipalId, setMergePrincipalId] = useState(null)
  const [mergeDuplicadoIds, setMergeDuplicadoIds] = useState([])
  const [mergeNombreFinal, setMergeNombreFinal] = useState('')
  const [showMergeModal, setShowMergeModal] = useState(false)
  const [mergeGroup, setMergeGroup] = useState(null)

  const [editingAlumno, setEditingAlumno] = useState(null)
  const [editNombre, setEditNombre] = useState('')
  const [editTelefono, setEditTelefono] = useState('')
  const [showEditAlumno, setShowEditAlumno] = useState(false)

  const [usuarios, setUsuarios] = useState([])
  const [showModalUsuario, setShowModalUsuario] = useState(false)
  const [editingUsuario, setEditingUsuario] = useState(null)
  const [formUsuarioEmail, setFormUsuarioEmail] = useState('')
  const [formUsuarioNombre, setFormUsuarioNombre] = useState('')
  const [formUsuarioPassword, setFormUsuarioPassword] = useState('')
  const [formUsuarioRol, setFormUsuarioRol] = useState('COACH')
  const [entrenadoresDisponibles, setEntrenadoresDisponibles] = useState([])
  const [formUsuarioEntrenadorId, setFormUsuarioEntrenadorId] = useState('')

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    Promise.all([
      apiFetch('/alumnos/').then(r => r.json()),
      apiFetch('/entrenadores/').then(r => r.json()),
      apiFetch('/horarios/').then(r => r.json()),
    ]).then(([al, ent, hor]) => {
      setAlumnos(al || [])
      setEntrenadores(ent || [])
      setHorarios(hor || [])
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setAlumnos([])
      setEntrenadores([])
      setHorarios([])
      setLoading(false)
    })
  }, [token])

  useEffect(() => {
    if (tab === 'usuarios' && isAdmin()) {
      cargarUsuarios()
    }
  }, [tab])

  useEffect(() => {
    if (tab === 'asistencia' && fecha && horarioId) {
      apiFetch(`/asistencia/?fecha=${fecha}&horario_id=${horarioId}`)
        .then(r => r.json())
        .then(data => setAsistenciasHoy(data))
    }
  }, [tab, fecha, horarioId])

  useEffect(() => {
    if (tab === 'entrenamientos') {
      setLoadingEntrenamientos(true)
      let url = `/entrenamientos/`
      const params = new URLSearchParams()
      if (filtroCategoria) params.append('categoria', filtroCategoria)
      if (filtroDia) params.append('dia', filtroDia)
      const qs = params.toString()
      if (qs) url += `?${qs}`
      apiFetch(url)
        .then(r => r.json())
        .then(data => setEntrenamientos(data))
        .finally(() => setLoadingEntrenamientos(false))
    }
  }, [tab, filtroCategoria, filtroDia])

  const alumnosPendientes = useMemo(() => {
    const idsAsistidos = new Set(asistenciasHoy.map(a => a.alumno_id))
    return alumnos.filter(a => a.activo && !idsAsistidos.has(a.id))
  }, [alumnos, asistenciasHoy])

  const alumnosFiltrados = useMemo(() => {
    if (!search.trim()) return alumnosPendientes
    const s = search.toLowerCase()
    return alumnosPendientes.filter(a => a.nombre_completo.toLowerCase().includes(s))
  }, [search, alumnosPendientes])

  const asistenciasAgrupadas = useMemo(() => {
    const mapa = new Map()
    for (const a of asistenciasHoy) {
      const key = `${a.alumno_id}-${a.fecha}-${a.horario_id}`
      if (!mapa.has(key)) {
        mapa.set(key, {
          alumno_id: a.alumno_id,
          alumno_nombre: a.alumno_nombre,
          fecha: a.fecha,
          horario_id: a.horario_id,
          horario_nombre: a.horario_nombre,
          entrenadores: [],
        })
      }
      mapa.get(key).entrenadores.push({
        id: a.id,
        entrenador_id: a.entrenador_id,
        entrenador_nombre: a.entrenador_nombre,
      })
    }
    return Array.from(mapa.values())
  }, [asistenciasHoy])

  const seleccionarHorario = (id) => {
    setHorarioId(id)
    setSelectedAlumno(null)
    setSelectedEntrenadorIds([])
    setEditingAlumnoKey(null)
    setEditEntrenadorIds([])
    setDeleteConfirmKey(null)
  }

  const seleccionarAlumno = (alumno) => {
    setSelectedAlumno(alumno)
    setSelectedEntrenadorIds([])
  }

  const abrirPerfilAlumno = async (alumno) => {
    setProfileAlumno(alumno)
    const r = await apiFetch(`/alumnos/${alumno.id}/entrenamientos/`)
    if (r.ok) {
      const data = await r.json()
      setProfileEntrenamientos(data)
    }
    setTab('perfil-alumno')
  }

  const toggleEntrenador = (id) => {
    setSelectedEntrenadorIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const confirmarEntrenadores = async () => {
    if (selectedEntrenadorIds.length === 0) {
      setToast('Selecciona al menos 1 entrenador')
      setTimeout(() => setToast(''), 2500)
      return
    }
    try {
      const res = await apiFetch('/asistencia/', {
        method: 'POST',
        body: JSON.stringify({
          alumno_id: selectedAlumno.id,
          entrenador_ids: selectedEntrenadorIds,
          horario_id: horarioId,
          fecha: fecha,
        }),
      })
      if (res.ok) {
        setToast(`Asistencia registrada: ${selectedAlumno.nombre_completo}`)
        setSelectedAlumno(null)
        setSelectedEntrenadorIds([])
        const r = await apiFetch(`/asistencia/?fecha=${fecha}&horario_id=${horarioId}`)
        const data = await r.json()
        setAsistenciasHoy(data)
        setTimeout(() => setToast(''), 2500)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al registrar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const abrirEditar = (grupo) => {
    setEditingAlumnoKey(`${grupo.alumno_id}-${grupo.fecha}-${grupo.horario_id}`)
    setEditEntrenadorIds(grupo.entrenadores.map(e => e.entrenador_id))
  }

  const toggleEditEntrenador = (id) => {
    setEditEntrenadorIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const guardarEdicion = async (grupo) => {
    if (editEntrenadorIds.length === 0) {
      setToast('Selecciona al menos 1 entrenador')
      setTimeout(() => setToast(''), 2500)
      return
    }
    try {
      const url = `/asistencia/alumno/${grupo.alumno_id}/fecha/${grupo.fecha}/horario/${grupo.horario_id}`
      const res = await apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify({ entrenador_ids: editEntrenadorIds }),
      })
      if (res.ok) {
        setToast('Entrenadores actualizados')
        setEditingAlumnoKey(null)
        setEditEntrenadorIds([])
        const r = await apiFetch(`/asistencia/?fecha=${fecha}&horario_id=${horarioId}`)
        const data = await r.json()
        setAsistenciasHoy(data)
        setTimeout(() => setToast(''), 2500)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al actualizar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const eliminarTodos = async (grupo) => {
    try {
      const url = `/asistencia/alumno/${grupo.alumno_id}/fecha/${grupo.fecha}/horario/${grupo.horario_id}`
      const res = await apiFetch(url, { method: 'DELETE' })
      if (res.ok) {
        setToast('Asistencia eliminada')
        setDeleteConfirmKey(null)
        const r = await apiFetch(`/asistencia/?fecha=${fecha}&horario_id=${horarioId}`)
        const data = await r.json()
        setAsistenciasHoy(data)
        setTimeout(() => setToast(''), 2500)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al eliminar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const eliminarIndividual = async (asistenciaId) => {
    try {
      const res = await apiFetch(`/asistencia/${asistenciaId}`, { method: 'DELETE' })
      if (res.ok) {
        setToast('Registro eliminado')
        setDeleteConfirmId(null)
        const r = await apiFetch(`/asistencia/?fecha=${fecha}&horario_id=${horarioId}`)
        const data = await r.json()
        setAsistenciasHoy(data)
        setTimeout(() => setToast(''), 2500)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al eliminar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const crearAlumno = async (e) => {
    e.preventDefault()
    if (!nuevoNombre.trim()) return
    try {
      const body = { nombre_completo: nuevoNombre.trim(), telefono: nuevoTelefono.trim() || null }
      if (isAdmin()) {
        body.entrenador_id = nuevoEntrenadorId ? Number(nuevoEntrenadorId) : undefined
      }
      const res = await apiFetch('/alumnos/', {
        method: 'POST',
        body: JSON.stringify(body),
      })
      if (res.ok) {
        const nuevo = await res.json()
        setAlumnos([...alumnos, nuevo])
        setNuevoNombre('')
        setNuevoTelefono('')
        setNuevoEntrenadorId('')
        setShowNuevoAlumno(false)
        setToast('Alumno creado')
        setTimeout(() => setToast(''), 2000)
      } else {
        const err = await res.json().catch(() => ({}))
        setToast(err.detail || 'Error al crear alumno')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error al crear alumno')
      setTimeout(() => setToast(''), 3000)
     }
   }

   const cargarUsuarios = async () => {
     if (!isAdmin()) return
     try {
       const res = await apiFetch('/users')
       if (res.ok) {
         setUsuarios(await res.json())
       }
     } catch {
     }
   }

   const cargarReporte = async () => {
    if (!reporteDesde || !reporteHasta) {
      setToast('Selecciona fecha desde y hasta')
      setTimeout(() => setToast(''), 2500)
      return
    }
    try {
      setReporte(null)
      setSeguimiento([])
      setCobertura([])
      setCarga([])
      setPorHorario([])
      setCumplimiento([])

      const qs = `desde=${reporteDesde}&hasta=${reporteHasta}`
      const endpoints = [
        `/reportes/asistencia-por-alumno?${qs}`,
        `/reportes/cobertura-entrenamientos?${qs}`,
        `/reportes/carga-entrenadores?${qs}`,
        `/reportes/asistencia-por-horario?${qs}`,
        `/reportes/cumplimiento-entrenamientos?${qs}`,
      ]

      const results = await Promise.allSettled(endpoints.map(url => apiFetch(url).then(r => {
        if (!r.ok) throw new Error(`Error ${r.status}`)
        return r.json()
      })))

      if (results[0].status === 'fulfilled') setSeguimiento(results[0].value)
      if (results[1].status === 'fulfilled') setCobertura(results[1].value)
      if (results[2].status === 'fulfilled') setCarga(results[2].value)
      if (results[3].status === 'fulfilled') setPorHorario(results[3].value)
      if (results[4].status === 'fulfilled') setCumplimiento(results[4].value)

      const fallos = results.filter(r => r.status === 'rejected')
      if (fallos.length > 0) {
        setToast(`${fallos.length} sección(es) con errores`)
        setTimeout(() => setToast(''), 3500)
      }
    } catch (e) {
      setToast('Error al generar reporte')
      setTimeout(() => setToast(''), 3500)
    }
  }

  const entrenamientosFiltrados = useMemo(() => {
    const q = busquedaEntrenamiento.trim().toLowerCase()
    return entrenamientos.filter(ent => {
      const matchCategoria = !filtroCategoria || ent.categoria === filtroCategoria
      const matchDia = !filtroDia || ent.dia_sugerido === filtroDia
      const matchBusqueda = !q || ent.nombre.toLowerCase().includes(q) || (ent.descripcion || '').toLowerCase().includes(q)
      return matchCategoria && matchDia && matchBusqueda
    })
  }, [entrenamientos, filtroCategoria, filtroDia, busquedaEntrenamiento])

  const statsEntrenamientos = useMemo(() => {
    const stats = { total: entrenamientos.length }
    CATEGORIAS.forEach(c => {
      stats[c] = entrenamientos.filter(e => e.categoria === c).length
    })
    return stats
  }, [entrenamientos])

  const abrirDetalleEntrenamiento = (ent) => {
    setEntrenamientoSeleccionado(ent)
    setShowDetalleEntrenamiento(true)
  }

  const abrirNuevoEntrenamiento = () => {
    setEditingEntrenamiento(null)
    setFormNombre('')
    setFormCategoria('tecnica')
    setFormDia('')
    setFormDescripcion('')
    setFormVideoUrl('')
    setFormThumbnail('')
    setFormDuracion('')
    setFormNivel('')
    setFormObjetivo('')
    setFormEquipamiento('')
    setFormEjercicios('')
    setShowModalEntrenamiento(true)
  }

  const abrirEditarEntrenamiento = (ent) => {
    setEditingEntrenamiento(ent)
    setFormNombre(ent.nombre)
    setFormCategoria(ent.categoria)
    setFormDia(ent.dia_sugerido || '')
    setFormDescripcion(ent.descripcion || '')
    setFormVideoUrl(ent.video_url || '')
    setFormThumbnail(ent.thumbnail || '')
    setFormDuracion(ent.duracion != null ? String(ent.duracion) : '')
    setFormNivel(ent.nivel || '')
    setFormObjetivo(ent.objetivo || '')
    setFormEquipamiento(ent.equipamiento || '')
    setFormEjercicios(ent.ejercicios || '')
    setShowModalEntrenamiento(true)
  }

  const guardarEntrenamiento = async (e) => {
    e.preventDefault()
    if (!formNombre.trim()) return
    try {
      const body = {
        nombre: formNombre.trim(),
        categoria: formCategoria,
        descripcion: formDescripcion.trim() || null,
        dia_sugerido: formDia || null,
        video_url: formVideoUrl.trim() || null,
        thumbnail: formThumbnail.trim() || null,
        duracion: Number(formDuracion) || null,
        nivel: formNivel || null,
        objetivo: formObjetivo.trim() || null,
        equipamiento: formEquipamiento.trim() || null,
        ejercicios: formEjercicios.trim() || null,
      }
      const url = editingEntrenamiento ? `/entrenamientos/${editingEntrenamiento.id}` : `/entrenamientos/`
      const method = editingEntrenamiento ? 'PUT' : 'POST'
      const res = await apiFetch(url, {
        method,
        body: JSON.stringify(body),
      })
      if (res.ok) {
        setToast(editingEntrenamiento ? 'Entrenamiento actualizado' : 'Entrenamiento creado')
        setShowModalEntrenamiento(false)
        setEditingEntrenamiento(null)
        let url2 = `/entrenamientos/`
        const params = new URLSearchParams()
        if (filtroCategoria) params.append('categoria', filtroCategoria)
        if (filtroDia) params.append('dia', filtroDia)
        const qs = params.toString()
        if (qs) url2 += `?${qs}`
        const r = await apiFetch(url2)
        const data = await r.json()
        setEntrenamientos(data)
        setTimeout(() => setToast(''), 2000)
      }
    } catch (e) {
      setToast('Error al guardar')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const confirmarEliminarEntrenamiento = async () => {
    if (!deleteConfirmEntrenamiento) return
    try {
      const res = await apiFetch(`/entrenamientos/${deleteConfirmEntrenamiento.id}`, { method: 'DELETE' })
      if (res.ok) {
        setToast('Entrenamiento desactivado')
        setDeleteConfirmEntrenamiento(null)
        let url = `/entrenamientos/`
        const params = new URLSearchParams()
        if (filtroCategoria) params.append('categoria', filtroCategoria)
        if (filtroDia) params.append('dia', filtroDia)
        const qs = params.toString()
        if (qs) url += `?${qs}`
        const r = await apiFetch(url)
        const data = await r.json()
        setEntrenamientos(data)
        setTimeout(() => setToast(''), 2000)
      } else if (res.status === 403) {
        setToast('No tienes permisos para realizar esta acción.')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error al eliminar')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const abrirNuevaAsignacion = () => {
    setEditingAsignacion(null)
    setFormEntrenamientoId('')
    setFormEntrenadorId('')
    setFormFecha(new Date().toISOString().split('T')[0])
    setFormEstado('planificado')
    setFormNotas('')
    setShowModalAsignar(true)
  }

  const abrirEditarAsignacion = (asig) => {
    setEditingAsignacion(asig)
    setFormEntrenamientoId(String(asig.entrenamiento_id))
    setFormEntrenadorId(asig.entrenador_id ? String(asig.entrenador_id) : '')
    setFormFecha(asig.fecha)
    setFormEstado(asig.estado)
    setFormNotas(asig.notas || '')
    setShowModalAsignar(true)
  }

  const guardarAsignacion = async (e) => {
    e.preventDefault()
    if (!profileAlumno || !formEntrenamientoId) return
    try {
      const body = {
        entrenamiento_id: Number(formEntrenamientoId),
        entrenador_id: formEntrenadorId ? Number(formEntrenadorId) : null,
        fecha: formFecha,
        estado: formEstado,
        notas: formNotas.trim() || null,
      }
      const url = `/alumnos/${profileAlumno.id}/entrenamientos/`
      const res = await apiFetch(url, {
        method: 'POST',
        body: JSON.stringify(body),
      })
      if (res.ok) {
        setToast(editingAsignacion ? 'Asignación actualizada' : 'Entrenamiento asignado')
        setShowModalAsignar(false)
        setEditingAsignacion(null)
        const r = await apiFetch(`/alumnos/${profileAlumno.id}/entrenamientos/`)
        if (r.ok) {
          const data = await r.json()
          setProfileEntrenamientos(data)
        }
        setTimeout(() => setToast(''), 2000)
      } else if (res.status === 403) {
        setToast('No tienes permisos para realizar esta acción.')
        setTimeout(() => setToast(''), 3000)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al guardar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const confirmarEliminarAsignacion = async () => {
    if (!deleteConfirmAsignacion || !profileAlumno) return
    try {
      const res = await apiFetch(`/alumnos/${profileAlumno.id}/entrenamientos/${deleteConfirmAsignacion.id}`, { method: 'DELETE' })
      if (res.ok) {
        setToast('Asignación eliminada')
        setDeleteConfirmAsignacion(null)
        const r = await apiFetch(`/alumnos/${profileAlumno.id}/entrenamientos/`)
        if (r.ok) {
          const data = await r.json()
          setProfileEntrenamientos(data)
        }
        setTimeout(() => setToast(''), 2000)
      }
    } catch (e) {
      setToast('Error al eliminar')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const abrirEliminarAlumno = async (alumno) => {
    setDeleteConfirmAlumno(alumno)
    try {
      const rAsis = await apiFetch(`/asistencia/alumno/${alumno.id}`)
      const asistencias = rAsis.ok ? await rAsis.json() : []
      const rEnt = await apiFetch(`/alumnos/${alumno.id}/entrenamientos/`)
      const entrenamientos = rEnt.ok ? await rEnt.json() : []
      setAlumnoDeleteStats({
        asistencias: asistencias.length,
        entrenamientos: entrenamientos.length,
      })
    } catch (e) {
      setAlumnoDeleteStats({ asistencias: 0, entrenamientos: 0 })
    }
  }

  const confirmarEliminarAlumno = async () => {
    if (!deleteConfirmAlumno) return
    try {
      const res = await apiFetch(`/alumnos/${deleteConfirmAlumno.id}`, { method: 'DELETE' })
      if (res.ok) {
        setToast('Alumno desactivado')
        setDeleteConfirmAlumno(null)
        setAlumnos(prev => prev.filter(a => a.id !== deleteConfirmAlumno.id))
        setTimeout(() => setToast(''), 2500)
      } else if (res.status === 403) {
        setToast('No tienes permisos para realizar esta acción.')
        setTimeout(() => setToast(''), 3000)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al eliminar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const abrirEditarAlumno = (alumno) => {
    setEditingAlumno(alumno)
    setEditNombre(alumno.nombre_completo)
    setEditTelefono(alumno.telefono || '')
    setShowEditAlumno(true)
  }

  const guardarEdicionAlumno = async (e) => {
    e.preventDefault()
    if (!editingAlumno || !editNombre.trim()) return
    try {
      const res = await apiFetch(`/alumnos/${editingAlumno.id}`, {
        method: 'PUT',
        body: JSON.stringify({ nombre_completo: editNombre.trim(), telefono: editTelefono.trim() || null }),
      })
      if (res.ok) {
        const actualizado = await res.json()
        setAlumnos(prev => prev.map(a => a.id === actualizado.id ? actualizado : a))
        setShowEditAlumno(false)
        setEditingAlumno(null)
        setToast('Alumno actualizado')
        setTimeout(() => setToast(''), 2000)
      } else if (res.status === 403) {
        setToast('No tienes permisos para realizar esta acción.')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error al actualizar')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const normalizarNombre = (nombre) => {
    return nombre
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, ' ')
      .trim()
  }

  const detectarDuplicados = async () => {
    try {
      const res = await apiFetch('/alumnos/?incluir_inactivos=true')
      if (!res.ok) return
      const todos = await res.json()
      const grupos = new Map()
      for (const a of todos) {
        const key = normalizarNombre(a.nombre_completo)
        if (!grupos.has(key)) grupos.set(key, [])
        grupos.get(key).push(a)
      }
      const dupes = Array.from(grupos.values()).filter(g => g.length > 1)
      setDuplicados(dupes)
      setShowDuplicados(true)
    } catch (e) {
      setToast('Error al detectar duplicados')
      setTimeout(() => setToast(''), 3000)
    }
  }

  const abrirMerge = (grupo) => {
    setMergeGroup(grupo)
    setMergePrincipalId(grupo[0].id)
    setMergeDuplicadoIds(grupo.slice(1).map(a => a.id))
    setMergeNombreFinal(grupo[0].nombre_completo)
    setShowMergeModal(true)
  }

  const toggleMergeDuplicado = (id) => {
    setMergeDuplicadoIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const confirmarMerge = async () => {
    if (!mergePrincipalId || mergeDuplicadoIds.length === 0) return
    try {
      const res = await apiFetch(`/alumnos/${mergePrincipalId}/fusionar`, {
        method: 'POST',
        body: JSON.stringify({
          ids_duplicados: mergeDuplicadoIds,
          nombre_final: mergeNombreFinal.trim() || undefined,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setToast(`${data.mensaje}: ${data.asistencias_reasignadas} asistencias, ${data.entrenamientos_reasignados} entrenamientos`)
        setShowMergeModal(false)
        setMergeGroup(null)
        setMergePrincipalId(null)
        setMergeDuplicadoIds([])
        setMergeNombreFinal('')
        const r = await apiFetch('/alumnos/?incluir_inactivos=true')
        const todos = await r.json()
        setAlumnos(todos.filter(a => a.activo))
        const grupos = new Map()
        for (const a of todos) {
          const key = normalizarNombre(a.nombre_completo)
          if (!grupos.has(key)) grupos.set(key, [])
          grupos.get(key).push(a)
        }
        const dupes = Array.from(grupos.values()).filter(g => g.length > 1)
        setDuplicados(dupes)
        setTimeout(() => setToast(''), 3500)
      } else if (res.status === 403) {
        setToast('No tienes permisos para realizar esta acción.')
        setTimeout(() => setToast(''), 3000)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Error al fusionar')
        setTimeout(() => setToast(''), 3000)
      }
    } catch (e) {
      setToast('Error de conexion')
      setTimeout(() => setToast(''), 3000)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen text-white text-xl">Cargando...</div>
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-boxing-dark text-white pb-24">
      <header className="bg-boxing-red py-4 px-4 shadow-lg sticky top-0 z-50">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <div className="text-center flex-1">
            <h1 className="text-2xl font-bold tracking-tight">BoxingClub Los Andes</h1>
            <p className="text-red-100 text-sm mt-1">Control de Asistencia</p>
          </div>
          {currentUser && (
            <button
              onClick={logout}
              className="text-xs text-red-100 hover:text-white border border-red-400/40 rounded-lg px-3 py-1.5"
              title="Cerrar sesión"
            >
              Salir
            </button>
          )}
        </div>
      </header>

      <nav className="flex border-b border-gray-700 sticky top-[72px] bg-boxing-dark z-40">
        <button
          onClick={() => setTab('alumnos')}
          className={`flex-1 py-3 text-center font-semibold text-sm ${tab === 'alumnos' || tab === 'perfil-alumno' ? 'text-boxing-red border-b-2 border-boxing-red' : 'text-gray-400'}`}
        >
          Alumnos
        </button>
        <button
          onClick={() => setTab('asistencia')}
          className={`flex-1 py-3 text-center font-semibold text-sm ${tab === 'asistencia' ? 'text-boxing-red border-b-2 border-boxing-red' : 'text-gray-400'}`}
        >
          Tomar Asistencia
        </button>
        <button
          onClick={() => setTab('entrenamientos')}
          className={`flex-1 py-3 text-center font-semibold text-sm ${tab === 'entrenamientos' ? 'text-boxing-red border-b-2 border-boxing-red' : 'text-gray-400'}`}
        >
          Entrenamientos
        </button>
        <button
          onClick={() => setTab('reportes')}
          className={`flex-1 py-3 text-center font-semibold text-sm ${tab === 'reportes' ? 'text-boxing-red border-b-2 border-boxing-red' : 'text-gray-400'}`}
        >
          Historial
        </button>
        {isAdmin() && (
          <button
            onClick={() => setTab('usuarios')}
            className={`flex-1 py-3 text-center font-semibold text-sm ${tab === 'usuarios' ? 'text-boxing-red border-b-2 border-boxing-red' : 'text-gray-400'}`}
          >
            Usuarios
          </button>
        )}
      </nav>

      {tab === 'asistencia' && (
        <div className="max-w-lg mx-auto px-4 mt-4 space-y-4">
          <div className="space-y-2">
            <label className="block text-sm text-gray-300 font-medium">Fecha</label>
            <input
              type="date"
              value={fecha}
              onChange={e => setFecha(e.target.value)}
              className="w-full bg-boxing-gray border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm text-gray-300 font-medium">Horario</label>
            <div className="grid grid-cols-3 gap-2">
              {horarios.map(h => (
                <button
                  key={h.id}
                  onClick={() => seleccionarHorario(h.id)}
                  className={`py-3 rounded-lg font-bold text-sm border-2 transition-all ${horarioId === h.id ? 'border-boxing-red bg-red-900/30 text-white' : 'border-gray-700 bg-boxing-gray text-gray-300'}`}
                >
                  {h.nombre.charAt(0).toUpperCase() + h.nombre.slice(1)}
                  <span className="block text-xs mt-1 opacity-80">{formatTime(h.hora_inicio)} - {formatTime(h.hora_fin)}</span>
                </button>
              ))}
            </div>
          </div>

          {horarioId && (
            <>
              <div className="space-y-2">
                <label className="block text-sm text-gray-300 font-medium">Alumno</label>
                <input
                  type="text"
                  placeholder="Buscar alumno..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="w-full bg-boxing-gray border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                />
                <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                  {alumnosFiltrados.map(a => (
                    <button
                      key={a.id}
                      onClick={() => seleccionarAlumno(a)}
                      className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-all ${selectedAlumno?.id === a.id ? 'border-boxing-red bg-red-900/30' : 'border-gray-700 bg-boxing-gray'}`}
                    >
                      <span className="font-medium">{a.nombre_completo}</span>
                      {a.telefono && <span className="block text-xs text-gray-400">{a.telefono}</span>}
                    </button>
                  ))}
                  {alumnosFiltrados.length === 0 && (
                    <p className="text-gray-500 text-sm text-center py-4">No hay alumnos pendientes para este horario</p>
                  )}
                </div>
              </div>

              {selectedAlumno && (
                <div className="space-y-2">
                  <label className="block text-sm text-gray-300 font-medium">Entrenadores</label>
                  <div className="bg-boxing-gray border border-gray-700 rounded-lg p-3 space-y-2">
                    {entrenadores.map(e => (
                      <label key={e.id} className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedEntrenadorIds.includes(e.id)}
                          onChange={() => toggleEntrenador(e.id)}
                          className="w-5 h-5 rounded border-gray-600 text-boxing-red focus:ring-boxing-red bg-boxing-dark"
                        />
                        <span className="text-white font-medium">{e.nombre}</span>
                      </label>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={confirmarEntrenadores}
                      disabled={selectedEntrenadorIds.length === 0}
                      className="flex-1 bg-boxing-red py-3 rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Confirmar
                    </button>
                    <button
                      onClick={() => { setSelectedAlumno(null); setSelectedEntrenadorIds([]) }}
                      className="flex-1 bg-gray-700 py-3 rounded-lg font-bold"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              )}
            </>
          )}

          <div className="space-y-2 pt-4">
            <h3 className="text-sm text-gray-400 font-medium uppercase tracking-wider">Ya asistieron hoy</h3>
            <div className="space-y-2">
              {asistenciasAgrupadas.map(grupo => {
                const key = `${grupo.alumno_id}-${grupo.fecha}-${grupo.horario_id}`
                const isEditing = editingAlumnoKey === key
                const isDeleteConfirm = deleteConfirmKey === key
                return (
                  <div key={key} className="bg-boxing-gray border border-gray-700 rounded-lg px-4 py-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <span className="font-medium">{grupo.alumno_nombre}</span>
                        <div className="text-xs text-gray-400 mt-1">
                          {grupo.entrenadores.map(e => e.entrenador_nombre).join(', ')}
                        </div>
                      </div>
                      <div className="flex gap-2 ml-2">
                        {isEditing ? (
                          <div className="flex gap-1 flex-wrap justify-end">
                            {entrenadores.map(e => (
                              <button
                                key={e.id}
                                onClick={() => toggleEditEntrenador(e.id)}
                                className={`px-2 py-1 rounded text-xs font-bold border ${editEntrenadorIds.includes(e.id) ? 'border-boxing-red bg-red-900/30 text-white' : 'border-gray-600 text-gray-300'}`}
                              >
                                {e.nombre.split(' ')[0]}
                              </button>
                            ))}
                            <button
                              onClick={() => guardarEdicion(grupo)}
                              className="px-2 py-1 rounded text-xs font-bold border border-green-600 text-green-400"
                            >
                              Guardar
                            </button>
                            <button
                              onClick={() => { setEditingAlumnoKey(null); setEditEntrenadorIds([]) }}
                              className="px-2 py-1 rounded text-xs font-bold border border-gray-600 text-gray-400"
                            >
                              Cancelar
                            </button>
                          </div>
                        ) : (
                          <>
                            <button
                              onClick={() => abrirEditar(grupo)}
                              className="text-gray-400 hover:text-white text-sm px-2 py-1"
                              title="Editar entrenadores"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={() => setDeleteConfirmKey(key)}
                              className="text-gray-400 hover:text-red-400 text-sm px-2 py-1"
                              title="Borrar todos"
                            >
                              🗑️
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                    {isDeleteConfirm && (
                      <div className="mt-3 bg-boxing-dark border border-gray-700 rounded-lg p-3 flex gap-2">
                        <p className="text-sm text-gray-300 flex-1">¿Quitar toda la asistencia de {grupo.alumno_nombre} en este horario?</p>
                        <button
                          onClick={() => setDeleteConfirmKey(null)}
                          className="px-3 py-1 rounded border border-gray-600 text-gray-300 text-sm font-bold"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={() => eliminarTodos(grupo)}
                          className="px-3 py-1 rounded bg-red-600 text-white text-sm font-bold"
                        >
                          Sí, quitar
                        </button>
                      </div>
                    )}
                  </div>
                )
              })}
              {asistenciasAgrupadas.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-2">Sin asistencias registradas</p>
              )}
            </div>
          </div>

           <button
             onClick={() => setShowNuevoAlumno(true)}
             className="fixed bottom-6 right-6 bg-boxing-red text-white w-14 h-14 rounded-full shadow-2xl text-3xl font-bold flex items-center justify-center hover:bg-red-700 transition-colors"
           >
             +
           </button>
         </div>
       )}

      {tab === 'reportes' && (
        <div className="max-w-lg mx-auto px-4 mt-4 space-y-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-3">
            <h3 className="font-bold text-lg">Filtros</h3>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Desde</label>
                <input type="date" value={reporteDesde} onChange={e => setReporteDesde(e.target.value)} className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-boxing-red" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Hasta</label>
                <input type="date" value={reporteHasta} onChange={e => setReporteHasta(e.target.value)} className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-boxing-red" />
              </div>
            </div>
            <button onClick={cargarReporte} className="w-full bg-boxing-red py-3 rounded-lg font-bold">Generar Reporte</button>
          </div>

          {cobertura.length > 0 && (
            <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-lg">🥊 Huecos en el entrenamiento</h3>
              <div className="space-y-2">
                {cobertura.map(c => (
                  <div key={c.alumno_id} className="bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3">
                    <span className="font-medium">{c.alumno_nombre}</span>
                    <span className="text-sm text-gray-400"> — nunca ha hecho: </span>
                    <span className="text-sm text-red-400 font-bold">{c.categorias_faltantes.join(', ')}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {porHorario.length > 0 && (
            <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-lg">🕐 Asistencia por horario</h3>
              <div className="space-y-2">
                {porHorario.map(h => (
                  <div key={h.horario_id} className="bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 flex items-center justify-between">
                    <span className="font-medium capitalize">{h.horario_nombre}</span>
                    <span className="bg-boxing-red text-white text-sm font-bold px-3 py-1 rounded-full">{h.total_asistencias} asistencias</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {cumplimiento.length > 0 && (
            <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-2">
              <h3 className="font-bold text-lg">✅ Cumplimiento de entrenamientos</h3>
              <div className="space-y-2">
                {cumplimiento.map(c => {
                  const tasa = c.tasa_cumplimiento
                  const texto = tasa === null ? 'sin datos' : `${Math.round(tasa * 100)}% (${c.realizados}/${c.planificados + c.realizados})`
                  const color = tasa === null ? 'text-gray-400' : tasa >= 0.8 ? 'text-green-400' : tasa >= 0.5 ? 'text-yellow-400' : 'text-red-400'
                  return (
                    <div key={c.alumno_id} className="bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 flex items-center justify-between">
                      <span className="font-medium">{c.alumno_nombre}</span>
                      <span className={`text-sm font-bold ${color}`}>{texto}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {cobertura.length === 0 && porHorario.length === 0 && cumplimiento.length === 0 && (
            <p className="text-gray-500 text-center py-6">Selecciona un rango y tocá Generar Reporte</p>
          )}
        </div>
      )}

      {tab === 'entrenamientos' && (
        <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 mt-4 space-y-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 sm:p-5 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-xl sm:text-2xl font-bold flex items-center gap-2">🥊 Entrenamientos</h2>
                <p className="text-xs sm:text-sm text-gray-400 mt-1">Biblioteca de ejercicios y sesiones de boxeo</p>
              </div>
              <button onClick={abrirNuevoEntrenamiento} className="bg-boxing-red text-white text-sm font-bold px-4 py-2.5 rounded-lg w-full sm:w-auto">
                + Nuevo entrenamiento
              </button>
            </div>

            <div className="relative">
              <input
                type="text"
                placeholder="🔎 Buscar entrenamiento..."
                value={busquedaEntrenamiento}
                onChange={e => setBusquedaEntrenamiento(e.target.value)}
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔎</span>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-gray-400 font-medium">{statsEntrenamientos.total} entrenamientos</span>
                <span className="text-xs text-gray-500">·</span>
                <span className="text-xs text-gray-400">{statsEntrenamientos.tecnica || 0} técnica</span>
              </div>
              <div className="flex bg-boxing-dark rounded-lg border border-gray-700 overflow-hidden">
                <button
                  onClick={() => setVistaEntrenamientos('grid')}
                  className={`px-3 py-1.5 text-xs font-bold ${vistaEntrenamientos === 'grid' ? 'bg-boxing-red text-white' : 'text-gray-400 hover:text-white'}`}
                  title="Vista grid"
                >
                  ▦
                </button>
                <button
                  onClick={() => setVistaEntrenamientos('lista')}
                  className={`px-3 py-1.5 text-xs font-bold ${vistaEntrenamientos === 'lista' ? 'bg-boxing-red text-white' : 'text-gray-400 hover:text-white'}`}
                  title="Vista lista"
                >
                  ☰
                </button>
              </div>
            </div>
          </div>

          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 sm:p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400 font-medium uppercase tracking-wider">Categorías</span>
              {(filtroCategoria || filtroDia) && (
                <button
                  onClick={() => { setFiltroCategoria(''); setFiltroDia('') }}
                  className="text-xs text-boxing-red font-bold"
                >
                  Limpiar
                </button>
              )}
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
              <button
                onClick={() => setFiltroCategoria('')}
                className={`px-3 py-1.5 rounded-full text-xs font-bold border whitespace-nowrap transition-all ${!filtroCategoria ? 'bg-white text-black border-white' : 'bg-boxing-dark text-gray-300 border-gray-700 hover:border-gray-500'}`}
              >
                Todos
              </button>
              {CATEGORIAS.map(c => (
                <button
                  key={c}
                  onClick={() => setFiltroCategoria(filtroCategoria === c ? '' : c)}
                  className={`px-3 py-1.5 rounded-full text-xs font-bold border whitespace-nowrap transition-all ${filtroCategoria === c ? `${CATEGORIAS_COLORES[c]} border-current` : 'bg-boxing-dark text-gray-300 border-gray-700 hover:border-gray-500'}`}
                >
                  {CATEGORIAS_ICONOS[c]} {c.charAt(0).toUpperCase() + c.slice(1)}
                </button>
              ))}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Día sugerido</label>
              <select
                value={filtroDia}
                onChange={e => setFiltroDia(e.target.value)}
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-boxing-red"
              >
                <option value="">Todos</option>
                {DIAS.map(d => (
                  <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          {loadingEntrenamientos ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-boxing-red border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : entrenamientosFiltrados.length === 0 ? (
            <div className="text-center py-12 space-y-2">
              <div className="text-4xl">🥊</div>
              <p className="text-gray-300 font-medium">No hay entrenamientos disponibles</p>
              <p className="text-gray-500 text-sm">Prueba cambiando los filtros o crea un nuevo entrenamiento.</p>
            </div>
          ) : vistaEntrenamientos === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {entrenamientosFiltrados.map(ent => (
                <div key={ent.id} className="bg-boxing-gray border border-gray-700 rounded-xl overflow-hidden hover:border-boxing-red/50 transition-colors group">
                  <div className="relative aspect-video bg-boxing-dark border-b border-gray-700 flex items-center justify-center overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    <div className="text-center z-10">
                      <div className="text-3xl sm:text-4xl mb-2">{CATEGORIAS_ICONOS[ent.categoria] || '📦'}</div>
                      <p className="text-xs text-gray-300 font-medium px-4 line-clamp-2">{ent.nombre}</p>
                    </div>
                    <button
                      onClick={() => abrirDetalleEntrenamiento(ent)}
                      className="absolute inset-0 z-20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Ver entrenamiento"
                    >
                      <span className="w-12 h-12 sm:w-14 sm:h-14 bg-boxing-red/90 rounded-full flex items-center justify-center text-white shadow-lg">
                        <span className="ml-1 text-lg">▶</span>
                      </span>
                    </button>
                    <div className="absolute top-2 right-2 z-30">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${ent.activo ? 'bg-green-900/60 text-green-300 border-green-700' : 'bg-gray-700 text-gray-400 border-gray-600'}`}>
                        {ent.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </div>
                  </div>
                  <div className="p-3 sm:p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${CATEGORIAS_COLORES[ent.categoria] || CATEGORIAS_COLORES.otro}`}>
                        {CATEGORIAS_ICONOS[ent.categoria] || '📦'} {ent.categoria}
                      </span>
                      {ent.dia_sugerido && (
                        <span className="text-[10px] text-gray-400">📅 {formatDayName(ent.dia_sugerido)}</span>
                      )}
                    </div>
                    {ent.descripcion && (
                      <p className="text-xs text-gray-400 line-clamp-2">{ent.descripcion}</p>
                    )}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-700">
                      <button
                        onClick={() => abrirDetalleEntrenamiento(ent)}
                        className="text-xs text-boxing-red font-bold hover:text-red-400 transition-colors"
                      >
                        Ver entrenamiento
                      </button>
                      <div className="flex gap-1">
                        <button
                          onClick={() => abrirEditarEntrenamiento(ent)}
                          className="text-gray-400 hover:text-white text-xs px-2 py-1 rounded border border-gray-700 hover:border-gray-500 transition-colors"
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => setDeleteConfirmEntrenamiento(ent)}
                          className="text-gray-400 hover:text-red-400 text-xs px-2 py-1 rounded border border-gray-700 hover:border-red-700 transition-colors"
                          title="Desactivar"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {entrenamientosFiltrados.map(ent => (
                <div key={ent.id} className="bg-boxing-gray border border-gray-700 rounded-xl p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center gap-3 hover:border-boxing-red/50 transition-colors">
                  <div className="w-full sm:w-20 h-40 sm:h-20 bg-boxing-dark rounded-lg border border-gray-700 flex items-center justify-center flex-shrink-0">
                    <span className="text-4xl sm:text-2xl">{CATEGORIAS_ICONOS[ent.categoria] || '📦'}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-bold text-sm truncate">{ent.nombre}</h4>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex-shrink-0 ${ent.activo ? 'bg-green-900/60 text-green-300 border-green-700' : 'bg-gray-700 text-gray-400 border-gray-600'}`}>
                        {ent.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${CATEGORIAS_COLORES[ent.categoria] || CATEGORIAS_COLORES.otro}`}>
                        {ent.categoria}
                      </span>
                      {ent.dia_sugerido && (
                        <span className="text-[10px] text-gray-400">📅 {formatDayName(ent.dia_sugerido)}</span>
                      )}
                    </div>
                    {ent.descripcion && (
                      <p className="text-xs text-gray-400 mt-1 line-clamp-1">{ent.descripcion}</p>
                    )}
                  </div>
                  <div className="flex sm:flex-col gap-1 flex-shrink-0">
                    <button
                      onClick={() => abrirDetalleEntrenamiento(ent)}
                      className="text-[10px] text-boxing-red font-bold hover:text-red-400 px-2 py-1 rounded border border-transparent hover:border-red-900 transition-colors"
                      title="Ver"
                    >
                      Ver
                    </button>
                    <button
                      onClick={() => abrirEditarEntrenamiento(ent)}
                      className="text-gray-400 hover:text-white text-xs px-2 py-1 rounded border border-gray-700 hover:border-gray-500 transition-colors"
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => setDeleteConfirmEntrenamiento(ent)}
                      className="text-gray-400 hover:text-red-400 text-xs px-2 py-1 rounded border border-gray-700 hover:border-red-700 transition-colors"
                      title="Desactivar"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
       )}

      {tab === 'usuarios' && isAdmin() && (
        <div className="max-w-lg mx-auto px-4 mt-4 space-y-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg">Usuarios</h3>
              <button
                onClick={() => {
                  setEditingUsuario(null)
                  setFormUsuarioEmail('')
                  setFormUsuarioNombre('')
                  setFormUsuarioPassword('')
                  setFormUsuarioRol('COACH')
                  setShowModalUsuario(true)
                  if (entrenadoresDisponibles.length === 0) {
                    apiFetch('/entrenadores/disponibles-para-coach')
                      .then(r => r.ok ? r.json() : [])
                      .then(setEntrenadoresDisponibles)
                  }
                }}
                className="bg-boxing-red text-white text-sm font-bold px-4 py-2 rounded-lg"
              >
                + Nuevo
              </button>
            </div>
            <div className="space-y-2">
              {usuarios.map(u => (
                <div key={u.id} className="bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 flex items-center justify-between">
                  <div className="flex-1">
                    <span className="font-medium">{u.nombre_completo}</span>
                    <span className="block text-xs text-gray-400">{u.email}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 inline-block ${u.role === 'ADMIN' ? 'bg-purple-900/60 text-purple-300 border border-purple-700' : 'bg-emerald-900/60 text-emerald-300 border border-emerald-700'}`}>
                      {u.role}
                    </span>
                  </div>
                  <div className="flex gap-2 ml-2">
                    <button
                      onClick={() => {
                        setEditingUsuario(u)
                        setFormUsuarioEmail(u.email)
                        setFormUsuarioNombre(u.nombre_completo)
                        setFormUsuarioPassword('')
                        setFormUsuarioRol(u.role)
                        setShowModalUsuario(true)
                      }}
                      className="text-gray-400 hover:text-white text-sm px-2 py-1 border border-gray-600 rounded"
                      title="Editar"
                    >
                      ✏️
                    </button>
                    {u.role === 'ADMIN' ? (
                      <span className="text-gray-400 text-xs px-2 py-1" title="Admin protegido">🔒</span>
                    ) : u.activo ? (
                      <button
                        onClick={async () => {
                          await apiFetch(`/users/${u.id}/deactivate`, { method: 'PATCH' })
                          cargarUsuarios()
                        }}
                        className="text-gray-400 hover:text-yellow-400 text-sm px-2 py-1 border border-gray-600 rounded"
                        title="Desactivar"
                      >
                        ⏸️
                      </button>
                    ) : (
                      <button
                        onClick={async () => {
                          await apiFetch(`/users/${u.id}/activate`, { method: 'PATCH' })
                          cargarUsuarios()
                        }}
                        className="text-gray-400 hover:text-green-400 text-sm px-2 py-1 border border-gray-600 rounded"
                        title="Activar"
                      >
                        ▶️
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {usuarios.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">No hay usuarios</p>
              )}
            </div>
          </div>

          {showModalUsuario && (
            <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
              <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
                <h3 className="text-lg font-bold mb-4">{editingUsuario ? 'Editar Usuario' : 'Nuevo Usuario'}</h3>
                <form onSubmit={async (e) => {
                  e.preventDefault()
                  if (!formUsuarioEmail.trim() || !formUsuarioNombre.trim()) return
                  if (!editingUsuario && !formUsuarioPassword.trim()) {
                    setToast('Debes establecer una contraseña')
                    setTimeout(() => setToast(''), 2000)
                    return
                  }
                  const body = {
                    email: formUsuarioEmail.trim(),
                    nombre_completo: formUsuarioNombre.trim(),
                    role: formUsuarioRol,
                  }
                  if (!editingUsuario) {
                    body.password = formUsuarioPassword
                  }
                  const url = editingUsuario ? `/users/${editingUsuario.id}` : `/users`
                  const res = await apiFetch(url, {
                    method: editingUsuario ? 'PUT' : 'POST',
                    body: JSON.stringify(body),
                  })
                  if (res.ok) {
                    setShowModalUsuario(false)
                    setEditingUsuario(null)
                    cargarUsuarios()
                  } else if (res.status === 403) {
                    setToast('No tienes permisos para realizar esta acción.')
                    setTimeout(() => setToast(''), 3000)
                  } else {
                    const err = await res.json()
                    setToast(err.detail || 'Error al guardar')
                    setTimeout(() => setToast(''), 3000)
                  }
                }} className="space-y-3">
                  <input
                    type="email"
                    placeholder="Correo *"
                    value={formUsuarioEmail}
                    onChange={e => setFormUsuarioEmail(e.target.value)}
                    required
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                  />
                  <input
                    type="text"
                    placeholder="Nombre completo *"
                    value={formUsuarioNombre}
                    onChange={e => setFormUsuarioNombre(e.target.value)}
                    required
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                  />
                  {!editingUsuario && (
                    <input
                      type="password"
                      placeholder="Contraseña *"
                      value={formUsuarioPassword}
                      onChange={e => setFormUsuarioPassword(e.target.value)}
                      required
                      className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                    />
                  )}
                  <select
                    value={formUsuarioRol}
                    onChange={e => setFormUsuarioRol(e.target.value)}
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                  >
                    <option value="COACH">COACH</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                  <div className="flex gap-2">
                    <button type="submit" className="flex-1 bg-boxing-red py-3 rounded-lg font-bold">Guardar</button>
                    <button type="button" onClick={() => { setShowModalUsuario(false); setEditingUsuario(null) }} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'alumnos' && !profileAlumno && (
        <div className="max-w-lg mx-auto px-4 mt-4 space-y-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg">Alumnos</h3>
              <button
                onClick={() => setShowNuevoAlumno(true)}
                className="bg-boxing-red text-white text-sm font-bold px-4 py-2 rounded-lg"
              >
                + Nuevo
              </button>
            </div>
            <div className="space-y-2">
              {alumnos.filter(a => a.activo).map(a => (
                <div key={a.id} className="bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 flex items-center justify-between">
                  <div className="flex-1">
                    <span className="font-medium">{a.nombre_completo}</span>
                    {a.telefono && <span className="block text-xs text-gray-400">{a.telefono}</span>}
                  </div>
                  <div className="flex gap-2 ml-2">
                    <button
                      onClick={() => abrirPerfilAlumno(a)}
                      className="text-gray-400 hover:text-white text-xs px-2 py-1 border border-gray-600 rounded"
                      title="Perfil"
                    >
                      👤
                    </button>
                    <button
                      onClick={() => abrirEditarAlumno(a)}
                      className="text-gray-400 hover:text-white text-xs px-2 py-1 border border-gray-600 rounded"
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => abrirEliminarAlumno(a)}
                      className="text-gray-400 hover:text-red-400 text-xs px-2 py-1 border border-gray-600 rounded"
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
              {alumnos.filter(a => a.activo).length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">No hay alumnos activos</p>
              )}
            </div>
          </div>

          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg">🔍 Duplicados</h3>
              <button onClick={detectarDuplicados} className="bg-gray-700 text-white text-sm font-bold px-4 py-2 rounded-lg">
                Detectar
              </button>
            </div>
            {showDuplicados && (
              <div className="space-y-2">
                {duplicados.length === 0 && (
                  <p className="text-gray-400 text-sm">No se detectaron duplicados</p>
                )}
                {duplicados.map((grupo, idx) => (
                  <div key={idx} className="bg-boxing-dark border border-gray-700 rounded-lg p-3 space-y-2">
                    <p className="text-sm text-gray-300 font-medium">"{grupo[0].nombre_completo}" ({grupo.length} registros)</p>
                    <div className="space-y-1">
                      {grupo.map(a => (
                        <div key={a.id} className="flex items-center justify-between text-sm">
                          <span className="text-gray-400">{a.nombre_completo} <span className="text-xs text-gray-500">(id: {a.id})</span></span>
                          <span className={`text-xs px-2 py-0.5 rounded ${a.id === grupo[0].id ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                            {a.id === grupo[0].id ? 'Principal' : 'Duplicado'}
                          </span>
                        </div>
                      ))}
                    </div>
                    <button
                      onClick={() => abrirMerge(grupo)}
                      className="w-full bg-boxing-red text-white text-sm font-bold py-2 rounded-lg"
                    >
                      Fusionar bajo "{grupo[0].nombre_completo}"
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'perfil-alumno' && profileAlumno && (
        <div className="max-w-lg mx-auto px-4 mt-4 space-y-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{profileAlumno.nombre_completo}</h3>
                <p className="text-xs text-gray-400 mt-1">
                  Activo desde: {new Date(profileAlumno.fecha_registro).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })}
                </p>
              </div>
              <button
                onClick={() => { setProfileAlumno(null); setTab('alumnos') }}
                className="text-gray-400 hover:text-white text-sm px-3 py-2 border border-gray-600 rounded-lg"
              >
                Volver
              </button>
            </div>
          </div>

          <button onClick={abrirNuevaAsignacion} className="w-full bg-boxing-red py-3 rounded-lg font-bold">+ Asignar Entrenamiento</button>

          <div className="space-y-2">
            <h3 className="text-sm text-gray-400 font-medium uppercase tracking-wider">Historial de entrenamientos</h3>
            {profileEntrenamientos.map(asig => {
              const ent = entrenamientos.find(e => e.id === asig.entrenamiento_id)
              const entNombre = ent ? ent.nombre : 'Entrenamiento eliminado'
              const esRealizado = asig.estado === 'realizado'
              const entrenador = entrenadores.find(e => e.id === asig.entrenador_id)
              return (
                <div key={asig.id} className="bg-boxing-gray border border-gray-700 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${esRealizado ? 'text-green-400' : 'text-yellow-400'}`}>
                        {esRealizado ? '✅ Realizado' : '📅 Planificado'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(asig.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => abrirEditarAsignacion(asig)}
                        className="text-gray-400 hover:text-white text-sm px-2 py-1"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => setDeleteConfirmAsignacion(asig)}
                        className="text-gray-400 hover:text-red-400 text-sm px-2 py-1"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <h4 className="font-bold text-lg">{entNombre}</h4>
                  {entrenador && <p className="text-xs text-gray-400 mt-1">Entrenador: {entrenador.nombre}</p>}
                  {asig.notas && <p className="text-sm text-gray-300 mt-2 italic">"{asig.notas}"</p>}
                  {deleteConfirmAsignacion && deleteConfirmAsignacion.id === asig.id && (
                    <div className="mt-3 bg-boxing-dark border border-gray-700 rounded-lg p-3 flex gap-2">
                      <p className="text-sm text-gray-300 flex-1">¿Eliminar esta asignación?</p>
                      <button
                        onClick={() => setDeleteConfirmAsignacion(null)}
                        className="px-3 py-1 rounded border border-gray-600 text-gray-300 text-sm font-bold"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={confirmarEliminarAsignacion}
                        className="px-3 py-1 rounded bg-red-600 text-white text-sm font-bold"
                      >
                        Sí, eliminar
                      </button>
                    </div>
                  )}
                </div>
              )
            })}
            {profileEntrenamientos.length === 0 && (
              <p className="text-gray-500 text-center py-6">Sin entrenamientos asignados</p>
            )}
          </div>
        </div>
      )}

      {showModalEntrenamiento && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-4">{editingEntrenamiento ? 'Editar Entrenamiento' : 'Nuevo Entrenamiento'}</h3>
            <form onSubmit={guardarEntrenamiento} className="space-y-3">
              <div className="space-y-2">
                <p className="text-xs text-gray-400 uppercase tracking-wider">Información básica</p>
                <input
                  type="text"
                  placeholder="Nombre *"
                  value={formNombre}
                  onChange={e => setFormNombre(e.target.value)}
                  required
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                />
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={formCategoria}
                    onChange={e => setFormCategoria(e.target.value)}
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                  >
                    {CATEGORIAS.map(c => (
                      <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                    ))}
                  </select>
                  <select
                    value={formDia}
                    onChange={e => setFormDia(e.target.value)}
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                  >
                    <option value="">Ninguno</option>
                    {DIAS.map(d => (
                      <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                    ))}
                  </select>
                </div>
                <textarea
                  placeholder="Descripción"
                  value={formDescripcion}
                  onChange={e => setFormDescripcion(e.target.value)}
                  rows="3"
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red resize-none"
                />
              </div>

              <div className="space-y-2">
                <p className="text-xs text-gray-400 uppercase tracking-wider">Multimedia</p>
                <input
                  type="text"
                  placeholder="Video URL (YouTube)"
                  value={formVideoUrl}
                  onChange={e => setFormVideoUrl(e.target.value)}
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                />
                <input
                  type="text"
                  placeholder="Thumbnail URL"
                  value={formThumbnail}
                  onChange={e => setFormThumbnail(e.target.value)}
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                />
              </div>

              <div className="space-y-2">
                <p className="text-xs text-gray-400 uppercase tracking-wider">Características</p>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Duración (min)"
                    value={formDuracion}
                    onChange={e => setFormDuracion(e.target.value)}
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
                  />
                  <select
                    value={formNivel}
                    onChange={e => setFormNivel(e.target.value)}
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                  >
                    <option value="">Nivel</option>
                    {NIVELES.map(n => (
                      <option key={n} value={n}>{n.charAt(0).toUpperCase() + n.slice(1)}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs text-gray-400 uppercase tracking-wider">Plan de entrenamiento</p>
                <textarea
                  placeholder="Objetivo"
                  value={formObjetivo}
                  onChange={e => setFormObjetivo(e.target.value)}
                  rows="2"
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red resize-none"
                />
                <textarea
                  placeholder="Equipamiento (ej: guantes, manoplas, saco)"
                  value={formEquipamiento}
                  onChange={e => setFormEquipamiento(e.target.value)}
                  rows="2"
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red resize-none"
                />
                <textarea
                  placeholder="Ejercicios (ej: 1. Jab x20\n2. Cross x20)"
                  value={formEjercicios}
                  onChange={e => setFormEjercicios(e.target.value)}
                  rows="3"
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red resize-none"
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="flex-1 bg-boxing-red py-3 rounded-lg font-bold">Guardar</button>
                <button type="button" onClick={() => { setShowModalEntrenamiento(false); setEditingEntrenamiento(null) }} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDetalleEntrenamiento && entrenamientoSeleccionado && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-3 sm:p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl w-full max-w-4xl lg:max-w-5xl max-h-[90vh] overflow-y-auto flex flex-col lg:flex-row">
            <div className="relative w-full lg:w-1/2 aspect-video bg-boxing-dark border-b lg:border-b-0 lg:border-r border-gray-700 flex items-center justify-center overflow-hidden flex-shrink-0">
              {entrenamientoSeleccionado.video_url ? (
                <iframe
                  src={entrenamientoSeleccionado.video_url.replace('watch?v=', 'embed/').replace('youtu.be/', 'www.youtube.com/embed/')}
                  title={entrenamientoSeleccionado.nombre}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="absolute inset-0 w-full h-full"
                ></iframe>
              ) : entrenamientoSeleccionado.thumbnail ? (
                <img src={entrenamientoSeleccionado.thumbnail} alt={entrenamientoSeleccionado.nombre} className="absolute inset-0 w-full h-full object-cover" />
              ) : (
                <div className="text-center z-10 p-4">
                  <div className="text-5xl sm:text-6xl mb-3">{CATEGORIAS_ICONOS[entrenamientoSeleccionado.categoria] || '📦'}</div>
                  <p className="text-sm text-gray-300 font-medium">Video próximamente</p>
                </div>
              )}
              <button
                onClick={() => setShowDetalleEntrenamiento(false)}
                className="absolute top-2 right-2 z-30 w-8 h-8 bg-black/60 hover:bg-black/80 rounded-full flex items-center justify-center text-white text-sm font-bold border border-gray-600"
                title="Cerrar"
              >
                ✕
              </button>
              <span className={`absolute top-2 left-2 z-30 text-[10px] font-bold px-2 py-0.5 rounded-full border ${entrenamientoSeleccionado.activo ? 'bg-green-900/60 text-green-300 border-green-700' : 'bg-gray-700 text-gray-400 border-gray-600'}`}>
                {entrenamientoSeleccionado.activo ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <div className="p-4 sm:p-6 space-y-3 flex-1 overflow-y-auto">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${CATEGORIAS_COLORES[entrenamientoSeleccionado.categoria] || CATEGORIAS_COLORES.otro}`}>
                  {CATEGORIAS_ICONOS[entrenamientoSeleccionado.categoria] || '📦'} {entrenamientoSeleccionado.categoria}
                </span>
                {entrenamientoSeleccionado.dia_sugerido && (
                  <span className="text-xs text-gray-400">📅 {formatDayName(entrenamientoSeleccionado.dia_sugerido)}</span>
                )}
              </div>
              <h3 className="text-lg sm:text-xl font-bold">{entrenamientoSeleccionado.nombre}</h3>
              {entrenamientoSeleccionado.descripcion && (
                <div>
                  <p className="text-xs text-gray-400 uppercase mb-1">Descripción</p>
                  <p className="text-sm text-gray-300">{entrenamientoSeleccionado.descripcion}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-boxing-dark border border-gray-700 rounded-lg p-3 text-center">
                  <p className="text-[10px] text-gray-400 uppercase">Duración</p>
                  <p className="text-sm font-bold text-white">{entrenamientoSeleccionado.duracion ? `${entrenamientoSeleccionado.duracion} min` : '--'}</p>
                </div>
                <div className="bg-boxing-dark border border-gray-700 rounded-lg p-3 text-center">
                  <p className="text-[10px] text-gray-400 uppercase">Nivel</p>
                  <p className="text-sm font-bold text-white">{entrenamientoSeleccionado.nivel ? entrenamientoSeleccionado.nivel.charAt(0).toUpperCase() + entrenamientoSeleccionado.nivel.slice(1) : '--'}</p>
                </div>
              </div>
              {entrenamientoSeleccionado.objetivo && (
                <div>
                  <p className="text-xs text-gray-400 uppercase mb-1">Objetivo</p>
                  <p className="text-sm text-gray-300">{entrenamientoSeleccionado.objetivo}</p>
                </div>
              )}
              {entrenamientoSeleccionado.equipamiento && (
                <div>
                  <p className="text-xs text-gray-400 uppercase mb-1">Equipamiento</p>
                  <p className="text-sm text-gray-300">{entrenamientoSeleccionado.equipamiento}</p>
                </div>
              )}
              {entrenamientoSeleccionado.ejercicios && (
                <div>
                  <p className="text-xs text-gray-400 uppercase mb-1">Ejercicios</p>
                  <p className="text-sm text-gray-300 whitespace-pre-line">{entrenamientoSeleccionado.ejercicios}</p>
                </div>
              )}
              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => { setShowDetalleEntrenamiento(false); abrirEditarEntrenamiento(entrenamientoSeleccionado) }}
                  className="flex-1 bg-boxing-red py-3 rounded-lg font-bold text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => setShowDetalleEntrenamiento(false)}
                  className="flex-1 bg-gray-700 py-3 rounded-lg font-bold text-sm"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showModalAsignar && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-4">{editingAsignacion ? 'Editar Asignación' : 'Asignar Entrenamiento'}</h3>
            <form onSubmit={guardarAsignacion} className="space-y-3">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Entrenamiento</label>
                <select
                  value={formEntrenamientoId}
                  onChange={e => setFormEntrenamientoId(e.target.value)}
                  required
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                >
                  <option value="">Seleccionar...</option>
                  {entrenamientos.map(ent => (
                    <option key={ent.id} value={ent.id}>{ent.nombre}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Fecha</label>
                <input
                  type="date"
                  value={formFecha}
                  onChange={e => setFormFecha(e.target.value)}
                  required
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Estado</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" value="planificado" checked={formEstado === 'planificado'} onChange={e => setFormEstado(e.target.value)} className="text-boxing-red focus:ring-boxing-red" />
                    <span className="text-white text-sm">Planificado</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" value="realizado" checked={formEstado === 'realizado'} onChange={e => setFormEstado(e.target.value)} className="text-green-500 focus:ring-green-500" />
                    <span className="text-white text-sm">Realizado</span>
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Entrenador (opcional)</label>
                <select
                  value={formEntrenadorId}
                  onChange={e => setFormEntrenadorId(e.target.value)}
                  className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
                >
                  <option value="">Sin asignar</option>
                  {entrenadores.map(e => (
                    <option key={e.id} value={e.id}>{e.nombre}</option>
                  ))}
                </select>
              </div>
              <textarea
                placeholder="Notas (opcional)"
                value={formNotas}
                onChange={e => setFormNotas(e.target.value)}
                rows="3"
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red resize-none"
              />
              <div className="flex gap-2">
                <button type="submit" className="flex-1 bg-boxing-red py-3 rounded-lg font-bold">Guardar</button>
                <button type="button" onClick={() => { setShowModalAsignar(false); setEditingAsignacion(null) }} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteConfirmAlumno && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-2">⚠️ Eliminar Alumno</h3>
            <p className="text-sm text-gray-300 mb-4">
              ¿Está seguro que desea desactivar a <span className="font-bold text-white">"{deleteConfirmAlumno.nombre_completo}"</span>?
            </p>
            <div className="bg-boxing-dark border border-gray-700 rounded-lg p-3 mb-4 text-xs text-gray-400 space-y-1">
              <p>📌 Se conservará su historial para auditoría:</p>
              <p>• Asistencias: <span className="text-white font-bold">{alumnoDeleteStats.asistencias}</span></p>
              <p>• Entrenamientos: <span className="text-white font-bold">{alumnoDeleteStats.entrenamientos}</span></p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setDeleteConfirmAlumno(null)} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              <button onClick={confirmarEliminarAlumno} className="flex-1 bg-red-600 text-white py-3 rounded-lg font-bold">Sí, desactivar</button>
            </div>
          </div>
        </div>
      )}

      {showEditAlumno && editingAlumno && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-4">Editar Alumno</h3>
            <form onSubmit={guardarEdicionAlumno} className="space-y-3">
              <input
                type="text"
                placeholder="Nombre completo *"
                value={editNombre}
                onChange={e => setEditNombre(e.target.value)}
                required
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              />
              <input
                type="text"
                placeholder="Teléfono (opcional)"
                value={editTelefono}
                onChange={e => setEditTelefono(e.target.value)}
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              />
              <div className="flex gap-2">
                <button type="submit" className="flex-1 bg-boxing-red py-3 rounded-lg font-bold">Guardar</button>
                <button type="button" onClick={() => { setShowEditAlumno(false); setEditingAlumno(null) }} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showMergeModal && mergeGroup && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-2">🔀 Fusionar Duplicados</h3>
            <p className="text-sm text-gray-300 mb-3">
              Selecciona los registros a fusionar bajo <span className="font-bold text-white">"{mergeGroup[0]?.nombre_completo}"</span>:
            </p>
            <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
              {mergeGroup.map(a => (
                <label key={a.id} className="flex items-center gap-3 bg-boxing-dark border border-gray-700 rounded-lg p-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={a.id === mergePrincipalId || mergeDuplicadoIds.includes(a.id)}
                    disabled={a.id === mergePrincipalId}
                    onChange={() => {
                      if (a.id === mergePrincipalId) return
                      toggleMergeDuplicado(a.id)
                    }}
                    className="w-5 h-5 rounded border-gray-600 text-boxing-red focus:ring-boxing-red bg-boxing-dark"
                  />
                  <div className="flex-1">
                    <span className="text-white text-sm font-medium">{a.nombre_completo}</span>
                    <span className="block text-xs text-gray-500">id: {a.id}</span>
                  </div>
                  {a.id === mergePrincipalId && <span className="text-xs bg-green-900 text-green-300 px-2 py-0.5 rounded">Principal</span>}
                </label>
              ))}
            </div>
            <div className="space-y-2 mb-4">
              <label className="block text-xs text-gray-400">Nombre final (canónico)</label>
              <input
                type="text"
                value={mergeNombreFinal}
                onChange={e => setMergeNombreFinal(e.target.value)}
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-boxing-red"
              />
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowMergeModal(false)} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              <button onClick={confirmarMerge} disabled={mergeDuplicadoIds.length === 0} className="flex-1 bg-boxing-red py-3 rounded-lg font-bold disabled:opacity-50">Fusionar</button>
            </div>
          </div>
        </div>
      )}

      {showNuevoAlumno && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-boxing-gray border border-gray-700 rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-4">Nuevo Alumno</h3>
            <form onSubmit={crearAlumno} className="space-y-3">
              <input
                type="text"
                placeholder="Nombre completo *"
                value={nuevoNombre}
                onChange={e => setNuevoNombre(e.target.value)}
                required
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              />
              <input
                type="text"
                placeholder="Telefono (opcional)"
                value={nuevoTelefono}
                onChange={e => setNuevoTelefono(e.target.value)}
                className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              />
              {isAdmin() && (
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Entrenador *</label>
                  <select
                    value={nuevoEntrenadorId}
                    onChange={e => setNuevoEntrenadorId(e.target.value)}
                    required
                    className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-boxing-red"
                  >
                    <option value="">Seleccionar entrenador...</option>
                    {entrenadores.map(e => (
                      <option key={e.id} value={e.id}>{e.nombre}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="flex gap-2">
                <button type="submit" className="flex-1 bg-boxing-red py-3 rounded-lg font-bold">Guardar</button>
                <button type="button" onClick={() => { setShowNuevoAlumno(false); setNuevoEntrenadorId('') }} className="flex-1 bg-gray-700 py-3 rounded-lg font-bold">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-boxing-red text-white px-6 py-3 rounded-lg shadow-2xl z-50 text-sm font-bold animate-pulse">
          {toast}
        </div>
      )}
      </div>
    </ProtectedRoute>
  )
}

export default App
