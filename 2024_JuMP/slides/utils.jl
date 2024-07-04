begin
    include("/home/blegat/git/blegat.github.io/biblio.jl")
	Biblio.load!()
    function cite(keys::Vector{String})
        return "[" * join(Biblio.citation_key.([Biblio.BIB[key] for key in keys]), ", ") * "]"
    end
    cite(key::String) = Biblio.cite(Biblio.BIB[key])
    function _print_entry(io, key; links = false, kws...)
        Biblio.print_entry(io, key; links, kws...)
    end
	function bib(key::String; kws...)
		io = IOBuffer()
		println(io, "<p style=\"font-size:12px\">")
		_print_entry(io, key; kws...)
		println(io, "</p>")
		return HTML(String(take!(io)))
	end
	function bib(keys::Vector{String}; kws...)
		io = IOBuffer()
		println(io, "<p style=\"font-size:12px\">")
		for key in keys
			_print_entry(io, key; kws...)
			println(io, "<br/>")
		end
		println(io, "</p>")
		return HTML(String(take!(io)))
	end

function CenteredBoundedBox(str)
    xbearing, ybearing, width, height, xadvance, yadvance =
        Luxor.textextents(str)
    lcorner = Point(xbearing - width/2, ybearing)
    ocorner = Point(lcorner.x + width, lcorner.y + height)
    return BoundingBox(lcorner, ocorner)
end
function boxed(str::AbstractString, p)
	translate(p)
	sethue("lightgrey")
	poly(CenteredBoundedBox(str) + 5, action = :stroke, close=true)
	sethue("black")
	text(str, Point(0, 0), halign=:center)
	#settext("<span font='26'>$str</span>", halign="center", markup=true)
	origin()
end

    struct Cols{T<:Tuple}
        cols::T
        dims::Vector{Int}
    end
    function Cols(a::Tuple)
        n = length(a)
        return Cols(a, div(100, n) * ones(Int, n))
    end
    Cols(a, b, args...) = Cols(tuple(a, b, args...))

    function Base.show(io, mime::MIME"text/html", c::Cols)
        x = div(100, length(c.cols))
    	write(io, """<div style="display: flex; justify-content: center; align-items: center;">""")
        for (col, p) in zip(c.cols, c.dims)
            write(io, """<div style="flex: $p%;">""")
            show(io, mime, col)
            write(io, """</div>""")
        end
    	write(io, """</div>""")
    end
    function imgpath(file)
        if !('.' in file)
            file = file * ".png"
        end
        return joinpath("../../images/", file)
    end
    function img(file, args...)
        LocalResource(imgpath(file), args...)
    end
    section(t) = md"# $t"
    frametitle(t) = md"# $t" # with `##`, it's not centered
end
